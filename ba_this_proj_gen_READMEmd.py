with open('gen_READMEmd.py', 'w') as f:
    f.write('''#!/usr/bin/env python
# -*- coding utf-8 -*-

with open('README.md', 'w') as f:
    f.write(\"\"\"\
# SQLite Tool
================

A simple web-based SQLite tool for executing queries and viewing table data.

## Features
------------

* Execute arbitrary SQLite queries
* View table data in a HTML table format
* Create new tables
* Drop existing tables
* Insert new rows
* Sort table data by column

## Usage
-----

1. Run the script using Python (e.g. `python sqlite_tool.py`)
2. Open a web browser and navigate to `http://localhost:1025/`
3. Execute queries using the query form or click on the pre-defined buttons
4. View table data by clicking on the table names in the left-hand menu

## Requirements
---------------

* Python 3.x
* SQLite 3.x
* A web browser (e.g. Google Chrome, Mozilla Firefox)

## Note
-----

This script creates a SQLite database file named `database.db` in the current working directory. If you want to use an existing database file, modify the script accordingly.

## License
-------

This script is provided under the MIT License. See the LICENSE file for details.
\"\"\")
''')