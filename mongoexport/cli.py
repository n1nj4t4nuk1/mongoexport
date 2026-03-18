import argparse

from mongoexport import export_data
from mongoexport.logging_config import configure_logging


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export data from a MongoDB collection with pagination, delays, and retry logic."
    )

    parser.add_argument(
        "--uri",
        type=str,
        required=True,
        help="MongoDB Connection URI (e.g., mongodb://localhost:27017)",
    )
    parser.add_argument("--db", type=str, required=True, help="Database name")
    parser.add_argument("--collection", type=str, required=True, help="Collection name")

    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Number of documents per page/batch (default: 1000)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay in seconds between pages (default: 0.5)",
    )

    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of retries for a failed page fetch (default: 3)",
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=2.0,
        help="Delay in seconds before retrying a failed page (default: 2.0)",
    )

    parser.add_argument(
        "--output", type=str, default="output.json", help="Output file path (default: output.json)"
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point for the CLI."""
    configure_logging()
    args = parse_arguments()
    export_data(args)


if __name__ == "__main__":
    main()
