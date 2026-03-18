import argparse
import logging
import time
from typing import Any, Dict, List, Optional

from bson.json_util import dumps
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


def _fetch_batch_with_retries(
    collection: Any,
    last_id: Optional[Any],
    page_number: int,
    batch_size: int,
    retries: int,
    retry_delay: float,
) -> List[Dict[str, Any]]:
    attempt = 0

    while attempt < retries:
        try:
            logger.info(f"Fetching page {page_number} (starting after _id: {last_id})...")
            current_query: Dict[str, Any] = {}
            if last_id is not None:
                current_query["_id"] = {"$gt": last_id}

            cursor = collection.find(current_query).sort("_id", 1).limit(batch_size)
            return list(cursor)
        except PyMongoError as error:
            attempt += 1
            logger.error(f"Error fetching page {page_number} (Attempt {attempt}/{retries}): {error}")
            if attempt < retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.critical("Max retries reached. Aborting export.")
                raise

    return []


def export_data(args: argparse.Namespace) -> None:
    client = None
    try:
        logger.info(f"Connecting to MongoDB at {args.uri}...")
        client = MongoClient(args.uri)

        client.admin.command("ping")
        logger.info("Connected successfully.")

        db = client[args.db]
        collection = db[args.collection]

        last_id: Optional[Any] = None
        total_fetched = 0
        page_number = 1

        with open(args.output, "w", encoding="utf-8") as output_file:
            output_file.write("[")
            first_batch = True

            while True:
                documents = _fetch_batch_with_retries(
                    collection=collection,
                    last_id=last_id,
                    page_number=page_number,
                    batch_size=args.batch_size,
                    retries=args.retries,
                    retry_delay=args.retry_delay,
                )

                if not documents:
                    logger.info("No more documents found. Export complete.")
                    break

                if not first_batch:
                    output_file.write(",")

                json_str = dumps(documents)
                output_file.write(json_str[1:-1])
                output_file.flush()

                first_batch = False

                count = len(documents)
                total_fetched += count
                last_id = documents[-1]["_id"]

                logger.info(
                    f"Page {page_number} processed. {count} documents exported. Total: {total_fetched}"
                )

                page_number += 1

                if args.delay > 0:
                    time.sleep(args.delay)

            output_file.write("]")

        logger.info(f"Export finished. Total documents exported: {total_fetched}. Saved to {args.output}")
    except Exception as error:
        logger.error(f"An unexpected error occurred: {error}")
    finally:
        if client:
            client.close()
            logger.info("Connection closed.")
