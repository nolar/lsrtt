from __future__ import absolute_import

import click
import dill
from flask import current_app

from ._defaults import (
    DEFAULT_NOW,
    DEFAULT_DB_PATH,
    DEFAULT_LOAD_PATH,
    DEFAULT_DUMP_PATH,
    DEFAULT_MODEL_PATH,
    DEFAULT_LOAD_CHUNK_SIZE,
    DEFAULT_DUMP_CHUNK_SIZE,
    DEFAULT_PREDICT_CHUNK_SIZE,
)
from .db.connection import connect_db
from .db.load import load_orders
from .db.dump import dump_predictions
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
@click.option('--load-chunk-size', default=DEFAULT_LOAD_CHUNK_SIZE, type=int)
@click.option('--now', default=DEFAULT_NOW)
@click.option('--encoding', default='utf-8')
@click.argument('filename', default=DEFAULT_LOAD_PATH)
def load(filename, encoding, db_path, now, load_chunk_size):
    """
    Import the data from the source CSV file into the database.
    """
    with connect_db(db_path) as db:
        with open(filename, 'rt', encoding=encoding) as f:
            load_orders(db, f, now=now, load_chunk_size=load_chunk_size)


@lsrtt.command()
@click.option('--db-path', default=DEFAULT_DB_PATH)
@click.option('--dump-chunk-size', default=DEFAULT_DUMP_CHUNK_SIZE)
@click.argument('filename', default=DEFAULT_DUMP_PATH)
def dump(db_path, dump_chunk_size, filename):
    """
    Export the predictions from the database into the CSV file.
    """
    with connect_db(db_path) as db:
        with open(filename, 'wt', encoding='utf-8') as f:
            dump_predictions(db, f, export_chunk_size=dump_chunk_size)


@lsrtt.command()
@click.option('--db-path', default=DEFAULT_DB_PATH)
@click.option('--now', default=DEFAULT_NOW)
@click.option('--predict/--no-predict', default=False)
@click.option('--predict-chunk-size', default=DEFAULT_PREDICT_CHUNK_SIZE)
@click.option('--model', 'model_path', default=DEFAULT_MODEL_PATH)
def refresh(db_path, now, predict, predict_chunk_size, model_path):
    """
    Refresh the calculated fields that depend on the current date.

    It is better to call this command from crontab or another job scheduler.

    Note that there will be no automatic prediction of the customers' CLV,
    unless `--predict` is also added.
    This this done to give you better control on the DB maintenance steps.
    """
    with connect_db(db_path) as db:
        refresh_db(db, now)
        if predict:
            with open(model_path, 'rb') as model_file:
                model = dill.load(model_file)
            predict_db(db, model, predict_chunk_size=predict_chunk_size)


@lsrtt.command()
@click.option('--db-path', default=DEFAULT_DB_PATH)
@click.option('--predict-chunk-size', default=DEFAULT_PREDICT_CHUNK_SIZE)
@click.option('--model', 'model_path', default=DEFAULT_MODEL_PATH)
@click.option('--refresh/--no-refresh', default=False)
@click.option('--now', default=DEFAULT_NOW)
def predict(db_path, model_path, predict_chunk_size, refresh, now):
    """
    Calculate the predicted CLV.

    It is better to call this command from crontab or another job scheduler.

    Note that there will be no automatic refresh of the date-dependent fields,
    unless `--refresh` is also added.
    This this done to give you better control on the DB maintenance steps.
    """
    with connect_db(db_path) as db:
        if refresh:
            refresh_db(db, now)
        with open(model_path, 'rb') as model_file:
            model = dill.load(model_file)
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
