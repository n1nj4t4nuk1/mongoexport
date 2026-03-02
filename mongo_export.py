import argparse
import time
import json
import logging
from typing import Any, Dict, List, Optional
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson.json_util import dumps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments() -> argparse.Namespace:
    """
    Parses command line arguments.
    """
    parser = argparse.ArgumentParser(description="Export data from a MongoDB collection with pagination, delays, and retry logic.")

    # Connection parameters
    parser.add_argument("--uri", type=str, required=True, help="MongoDB Connection URI (e.g., mongodb://localhost:27017)")
    parser.add_argument("--db", type=str, required=True, help="Database name")
    parser.add_argument("--collection", type=str, required=True, help="Collection name")
    
    # Pagination and control parameters
    parser.add_argument("--batch-size", type=int, default=1000, help="Number of documents per page/batch (default: 1000)")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay in seconds between pages (default: 0.5)")
    
    # Retry parameters
    parser.add_argument("--retries", type=int, default=3, help="Number of retries for a failed page fetch (default: 3)")
    parser.add_argument("--retry-delay", type=float, default=2.0, help="Delay in seconds before retrying a failed page (default: 2.0)")
    
    # Output
    parser.add_argument("--output", type=str, default="output.json", help="Output file path (default: output.json)")

    return parser.parse_args()

def export_data(args: argparse.Namespace):
    """
    Main export logic.
    """
    client = None
    try:
        # Connect to MongoDB
        logger.info(f"Connecting to MongoDB at {args.uri}...")
        client = MongoClient(args.uri)
        
        # Verify connection
        client.admin.command('ping')
        logger.info("Connected successfully.")

        db = client[args.db]
        collection = db[args.collection]
        
        last_id = None
        total_fetched = 0
        page_number = 1
        
        # Open output file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write('[') # Start of JSON array
            first_batch = True

            while True:
                documents = []
                attempt = 0
                success = False

                while attempt < args.retries:
                    try:
                        logger.info(f"Fetching page {page_number} (starting after _id: {last_id})...")
                        current_query = {}
                        if last_id:
                            current_query['_id'] = {'$gt': last_id}
                        
                        cursor = collection.find(current_query).sort('_id', 1).limit(args.batch_size)
                        documents = list(cursor)
                        success = True
                        break
                    except PyMongoError as e:
                        attempt += 1
                        logger.error(f"Error fetching page {page_number} (Attempt {attempt}/{args.retries}): {e}")
                        if attempt < args.retries:
                            logger.info(f"Retrying in {args.retry_delay} seconds...")
                            time.sleep(args.retry_delay)
                        else:
                            logger.critical("Max retries reached. Aborting export.")
                            raise e

                if not documents:
                    logger.info("No more documents found. Export complete.")
                    break

                # Write batch to file
                if not first_batch:
                    f.write(',')
                
                # Convert batch to JSON string and write content (stripping outer brackets)
                json_str = dumps(documents)
                if len(documents) > 0:
                   f.write(json_str[1:-1])
                   f.flush()  # Force write to disk immediately

                first_batch = False

                count = len(documents)
                total_fetched += count
                last_id = documents[-1]['_id']
                
                logger.info(f"Page {page_number} processed. {count} documents exported. Total: {total_fetched}")
                
                page_number += 1
                
                # Delay between pages
                if args.delay > 0:
                    time.sleep(args.delay)

            f.write(']') # End of JSON array

        logger.info(f"Export finished. Total documents exported: {total_fetched}. Saved to {args.output}")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        if client:
            client.close()
            logger.info("Connection closed.")

if __name__ == "__main__":
    args = parse_arguments()
    export_data(args)
