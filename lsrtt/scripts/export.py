from __future__ import absolute_import

import click

from ._defaults import DEFAULT_DB_PATH, DEFAULT_MODEL_PATH, DEFAULT_RESULTS_PATH, DEFAULT_EXPORT_CHUNK_SIZE
from ..db.connection import connect_db
from ..db.exports import export_predictions


@click.command()
@click.option('--db-path', default=DEFAULT_DB_PATH)
@click.option('--export-chunk-size', default=DEFAULT_EXPORT_CHUNK_SIZE)
@click.option('--model', default=DEFAULT_MODEL_PATH)
@click.argument('filename', default=DEFAULT_RESULTS_PATH)
def export(db_path, model, export_chunk_size, filename):
    with connect_db(db_path) as db:
        with open(filename, 'wt', encoding='utf-8') as f:
            export_predictions(db, f, export_chunk_size=export_chunk_size)
