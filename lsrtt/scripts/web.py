from __future__ import absolute_import

import click
from flask import current_app

from ._defaults import DEFAULT_DB_PATH
from ..db.connection import connect_db
from ..web.app import app


@click.command()
@click.option('--db-path', default=DEFAULT_DB_PATH)
def web(db_path):
    # TODO: make a connection pool; NOW: a single db connection per thread for everything.
    with connect_db(db_path) as db:
        with app.app_context():
            # The path is used in the `get_db` in the app itself.
            current_app._database_path = db_path
        app.run(debug=True)
