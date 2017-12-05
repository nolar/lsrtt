import os.path

import dill
import numpy
import pytest


@pytest.fixture
def db():
    from lsrtt.db.connection import connect_db
    with connect_db(':memory:') as con:
        yield con


@pytest.fixture
def dbloader(db):
    def loader(table):
        c = db.cursor()
        c.execute('select * from {}'.format(table))
        return list(c.fetchall())
    return loader


@pytest.fixture
def model():
    model_path = os.path.join(os.path.dirname(__file__), 'model.dill')

    with open(model_path, 'rb') as model_file:
        model = dill.load(model_file)

    # FIXME: Workaround for buggy dill/dill-objects: requires the code dependencies in the main module, not locally.
    import __main__ as _main_module  # noqa
    _main_module.numpy = numpy

    return model
