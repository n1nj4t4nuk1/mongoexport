from mongocollector.cli import parse_arguments
from mongocollector.exporter import export_data
from mongocollector.logging_config import configure_logging


def main() -> None:
    configure_logging()
    args = parse_arguments()
    export_data(args)


if __name__ == "__main__":
    main()
