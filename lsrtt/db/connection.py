from __future__ import absolute_import

import contextlib
import sqlite3

DEFAULT_DB_PATH = 'db.sqlite'


@contextlib.contextmanager
def connect_db(db_path):
    with sqlite3.connect(db_path) as con:
        con.row_factory = dict_factory
        yield con


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
