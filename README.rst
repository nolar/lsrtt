=====
LSRTT
=====

LSRTT is...


Data import
===========

For the data storage, we use the sqlite3 database.
The database is by default located in the current working directory (can be configure with CLI options).

To import the data::

    convert orders.csv

To regularly refresh the fields that depend on the value of "now" (i.e. the current date),
execute once and/or put to the crontab or other scheduled job executor::

    refresh


Development
===========

To work on the source code locally with all the convenient tools::

    pip install -e .[dev]

This will also install the abovementioned scripts into the virtualenv's bin folder.
