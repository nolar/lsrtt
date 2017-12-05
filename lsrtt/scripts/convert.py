from __future__ import absolute_import

import click

from ._defaults import DEFAULT_DB_PATH, DEFAULT_CONVERT_CHUNK_SIZE, DEFAULT_NOW
from ..db.connection import connect_db
from ..db.convert import convert_to_db


@click.command()
@click.option('--db-path', default=DEFAULT_DB_PATH)
@click.option('--convert-chunk-size', default=DEFAULT_CONVERT_CHUNK_SIZE, type=int)
@click.option('--now', default=DEFAULT_NOW)
@click.option('--encoding', default='utf-8')
@click.argument('filename', default='orders.csv')
def convert(filename, encoding, db_path, now, convert_chunk_size):
    with connect_db(db_path) as db:
        with open(filename, 'rt', encoding=encoding) as f:
            convert_to_db(db, f, now=now, convert_chunk_size=convert_chunk_size)
