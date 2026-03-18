"""
Legacy entry point for mongoexport.
For new usage, please use the mongoexport CLI directly:
    mongoexport --uri <uri> --db <db> --collection <collection> ...
"""

from mongoexport.cli import main

if __name__ == "__main__":
    main()
