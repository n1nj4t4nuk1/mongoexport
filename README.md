# 🍃 mongoexport

Export data from MongoDB collections with advanced features like pagination, configurable delays, and automatic retry logic.

## Features

- **Paginated Export**: Efficiently export large collections using configurable batch sizes
- **Retry Logic**: Automatic retry mechanism with configurable attempts and delays
- **Configurable Delays**: Add delays between batches to avoid server overload
- **JSON Export**: Export data to JSON format using BSON serialization
- **CLI Tool**: Easy-to-use command-line interface
- **Robust Error Handling**: Comprehensive logging and error management

## Installation

### From PyPI

```bash
pip install mongoexport
```

### From Source

```bash
git clone https://github.com/yourusername/mongoexport.git
cd mongoexport
pip install -e .
```

## Usage

### Command Line

```bash
mongoexport \
  --uri mongodb://localhost:27017 \
  --db mydb \
  --collection mycollection \
  --batch-size 1000 \
  --delay 0.5 \
  --retries 3 \
  --retry-delay 2.0 \
  --output export.json
```

#### Option Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--uri` | string | required | MongoDB connection URI (e.g., `mongodb://localhost:27017`) |
| `--db` | string | required | Database name |
| `--collection` | string | required | Collection name |
| `--batch-size` | int | 1000 | Number of documents per batch |
| `--delay` | float | 0.5 | Delay in seconds between batches |
| `--retries` | int | 3 | Number of retry attempts for failed batches |
| `--retry-delay` | float | 2.0 | Delay in seconds before retrying |
| `--output` | string | output.json | Output file path |

### Python Module

```python
from mongoexport import export_data
import argparse

# Create arguments namespace
args = argparse.Namespace(
    uri="mongodb://localhost:27017",
    db="mydb",
    collection="mycollection",
    batch_size=1000,
    delay=0.5,
    retries=3,
    retry_delay=2.0,
    output="export.json"
)

# Export data
export_data(args)
```

## Requirements

- Python >= 3.8
- pymongo >= 3.12.0

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/mongoexport.git
cd mongoexport
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Issues

If you encounter any issues, please report them on [GitHub Issues](https://github.com/yourusername/mongoexport/issues).

## Changelog

### Version 0.1.0 (2026-03-18)
- Initial release
- Basic export functionality with pagination
- Retry logic with configurable delays
- CLI interface
