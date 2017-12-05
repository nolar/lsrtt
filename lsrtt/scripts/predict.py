from __future__ import absolute_import

import click

from ._defaults import DEFAULT_DB_PATH, DEFAULT_MODEL_PATH, DEFAULT_RESULTS_PATH, DEFAULT_PREDICT_CHUNK_SIZE
from ..db.connection import connect_db
from ..db.predict import predict_db


@click.command()
@click.option('--db-path', default=DEFAULT_DB_PATH)
@click.option('--predict-chunk-size', default=DEFAULT_PREDICT_CHUNK_SIZE)
@click.option('--model', default=DEFAULT_MODEL_PATH)
def predict(db_path, model, predict_chunk_size):
    with connect_db(db_path) as db:
        predict_db(db, model, predict_chunk_size=predict_chunk_size)
