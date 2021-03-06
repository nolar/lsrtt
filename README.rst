=====
LSRTT
=====

LSRTT is a sample ML app.

Brief intro::

    pip install .
    lsrtt --help

The typical worfklow for the manual prediction::

    lsrtt load      # ~20s
    lsrtt predict   # ~5s
    lsrtt dump      # ~2s

By default (without the command line options & arguments),
the data are loaded from ``./orders.csv`` (must be put into the local directory),
and dumped into ``./predictions.csv``.

For a regular service deployment, put the automatic data re-calculations into the scheduler/crontab::

    lsrtt refresh && lsrtt predict

To run a sample API web server::

    lsrtt web

The visit http://localhost:5000/ for more details. The supported API endpoints::

    curl http://localhost:5000/api/customers
    curl http://localhost:5000/api/customers/fffd7075b2a9034bf02202bf6cb5c63e/predictions


Development
===========

To work on the source code locally with all the convenient tools::

    pip install -e .[dev]

This will also install the abovementioned umbrella script into the virtualenv's bin folder.

To run the tests::

    pip install -e .[test]
    pytest
