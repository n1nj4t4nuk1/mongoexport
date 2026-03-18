"""Mongo collection export package.

A Python library to export MongoDB collections with pagination, retries, and configurable delays.

Example:
    >>> from mongoexport import export_data
    >>> import argparse
    >>> args = argparse.Namespace(
    ...     uri="mongodb://localhost:27017",
    ...     db="mydb",
    ...     collection="mycollection",
    ...     batch_size=1000,
    ...     delay=0.5,
    ...     retries=3,
    ...     retry_delay=2.0,
    ...     output="export.json"
    ... )
    >>> export_data(args)
"""

from mongoexport.exporter import export_data

__version__ = "0.1.0"
__author__ = "Javier Parada"
__email__ = "javierparada@pm.me"

__all__ = ["export_data"]
