from __future__ import absolute_import

import click

from ._defaults import DEFAULT_DB_PATH, DEFAULT_NOW
from ..db.connection import connect_db
from ..db.refresh import refresh_db


@click.command()
@click.option('--db-path', default=DEFAULT_DB_PATH)
@click.option('--now', default=DEFAULT_NOW)
def refresh(db_path, now):
    with connect_db(db_path) as db:
        refresh_db(db, now)
