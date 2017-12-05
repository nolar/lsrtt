from __future__ import absolute_import

import contextlib
import sqlite3

DEFAULT_DB_PATH = 'db.sqlite'


@contextlib.contextmanager
def connect_db(db_path):
    with sqlite3.connect(db_path) as con:
        yield con
