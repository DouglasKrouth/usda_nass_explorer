# usda_nass_explorer
Locally hosted tool that can be used to retrieve and analyze [USDA NASS data](https://www.nass.usda.gov/datasets/). WIP/fun project to practice displaying data in a local relational database (SQLite) with FastAPI and HTMX.

## Stack
* Written with `python 3.12.6` [link](https://www.python.org/downloads/release/python-3126/)
* managed with `poetry` [link](https://python-poetry.org/)
* tests implemented with `pytest` [link](https://docs.pytest.org/en/7.1.x/contents.html); note that test coverage for this project is minimal, would be easy to bolster with mocks for requests to external services.

## Components
### ./nass_io
* Generates a list of available USDA NASS download urls.
* Handles downloading the urls, writing files to disk.
* Methods to convert USDA NASS datasets into SQLite database files. 
    * NOTE: This has only been implemented for the `qs.census2002.txt.gz` dataset. Other schemas and ETL processes are nice-to-haves; reach out to me, create an issue, or submit a PR if you want to see additional functionality added.

### `Dockerfile` behavior
* The app's implemented such that the Dockerfile downloads the dataset from every time it's started. This is inefficient and could benefit from functionality that pulls `.txt.gz` or SQLite files from the users machine and uses those instead of downloading them.
    * TODO : Add ability to specify existing file argument to Docker on init to avoid users needing to download the file every time.
