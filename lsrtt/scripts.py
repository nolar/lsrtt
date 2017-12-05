from __future__ import absolute_import

import click
from flask import current_app

from ._defaults import (
    DEFAULT_NOW,
    DEFAULT_DB_PATH,
    DEFAULT_MODEL_PATH,
    DEFAULT_RESULTS_PATH,
    DEFAULT_PREDICT_CHUNK_SIZE,
    DEFAULT_CONVERT_CHUNK_SIZE,
    DEFAULT_EXPORT_CHUNK_SIZE,
)
from .db.connection import connect_db
from .db.convert import convert_to_db
from .db.exports import export_predictions
from .db.predict import predict_db
from .db.refresh import refresh_db
from .web.app import app


@click.group()
def lsrtt():
    """
    A sample ML prediction app.
    """
    pass


@lsrtt.command()
@click.option('--db-path', default=DEFAULT_DB_PATH)
@click.option('--convert-chunk-size', default=DEFAULT_CONVERT_CHUNK_SIZE, type=int)
@click.option('--now', default=DEFAULT_NOW)
@click.option('--encoding', default='utf-8')
@click.argument('filename', default='orders.csv')
def convert(filename, encoding, db_path, now, convert_chunk_size):
    """
    Import the data from the source CSV file into the database.
    """
    with connect_db(db_path) as db:
        with open(filename, 'rt', encoding=encoding) as f:
            convert_to_db(db, f, now=now, convert_chunk_size=convert_chunk_size)

@lsrtt.command()
@click.option('--db-path', default=DEFAULT_DB_PATH)
@click.option('--export-chunk-size', default=DEFAULT_EXPORT_CHUNK_SIZE)
@click.option('--model', default=DEFAULT_MODEL_PATH)
@click.argument('filename', default=DEFAULT_RESULTS_PATH)
def export(db_path, model, export_chunk_size, filename):
    """
    Export the predictions from the database into the CSV file.
    """
    with connect_db(db_path) as db:
        with open(filename, 'wt', encoding='utf-8') as f:
            export_predictions(db, f, export_chunk_size=export_chunk_size)


@lsrtt.command()
@click.option('--db-path', default=DEFAULT_DB_PATH)
@click.option('--now', default=DEFAULT_NOW)
def refresh(db_path, now):
    """
    Refresh the calculated fields that depend on the current date.

    It is better to call this command from crontab or another job scheduler.

    Note that there will be no automatic prediction of the customers' CLV,
    unless `--predict` is also added.
    This this done to give you better control on the DB maintenance steps.
    """
    with connect_db(db_path) as db:
        refresh_db(db, now)


@lsrtt.command()
@click.option('--db-path', default=DEFAULT_DB_PATH)
@click.option('--predict-chunk-size', default=DEFAULT_PREDICT_CHUNK_SIZE)
@click.option('--model', default=DEFAULT_MODEL_PATH)
def predict(db_path, model, predict_chunk_size):
    """
    Calculate the predicted CLV.

    It is better to call this command from crontab or another job scheduler.

    Note that there will be no automatic refresh of the date-dependent fields,
    unless `--refresh` is also added.
    This this done to give you better control on the DB maintenance steps.
    """
    with connect_db(db_path) as db:
        predict_db(db, model, predict_chunk_size=predict_chunk_size)


@lsrtt.command()
@click.option('--db-path', default=DEFAULT_DB_PATH)
def web(db_path):
    """
    Run a simple web server with the API access to the database.

    Available API endpoints:

        /api/customers
        /api/customers/fffd7075b2a9034bf02202bf6cb5c63e/predictions

    For more info, visit the index page in the web browser.
    """
    # TODO: make a connection pool; NOW: a single db connection per thread for everything.
    with connect_db(db_path) as db:
        with app.app_context():
            # The path is used in the `get_db` in the app itself.
            current_app._database_path = db_path
        app.run(debug=True)
