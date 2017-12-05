from __future__ import absolute_import

import contextlib
import sqlite3

DEFAULT_DB_PATH = 'db.sqlite'


@contextlib.contextmanager
def connect_db(db_path):
    with sqlite3.connect(db_path) as con:
        con.row_factory = _row_factory
        yield con


def _row_factory(cursor, row):
    return _row(fields=[col[0] for col in cursor.description], values=row)


class _row(list):
    """
    The row behaves as a regular list/tuple, but exposes the fields as attrs.
    """

    def __init__(self, fields, values):
        super(_row, self).__init__(values)
        self.__fields = fields

    def __repr__(self):
        values = super(_row, self).__repr__()
        return '{}({}, {})'.format(self.__class__.__name__, values, self.__fields)

    def __getattr__(self, name):
        try:
            idx = self.__fields.index(name)
        except ValueError:
            raise AttributeError("The row does not have {!r} field.".format(name))
        else:
            return self[idx]

