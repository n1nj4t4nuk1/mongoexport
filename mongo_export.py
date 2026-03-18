from mongoexport.cli import parse_arguments
from mongoexport.exporter import export_data
from mongoexport.logging_config import configure_logging


def main() -> None:
    configure_logging()
    args = parse_arguments()
    export_data(args)


if __name__ == "__main__":
    main()
