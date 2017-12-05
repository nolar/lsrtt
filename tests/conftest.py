import io
import os
import os.path
import tempfile

import dill
import numpy
import pytest

import lsrtt.web.app

CUSTOMER_ID = '123456789012345678901234567890ab'
CUSTOMER_CLV = 112.03
CSV = """
customer_id,order_id,order_item_id,num_items,revenue,created_at_date
123456789012345678901234567890ab,4662083,21257304,1,24.79,2017-09-01
d0d7a76fea3729a9381d39aca78b52d3,4655291,21224156,1,22.68,2017-09-01
450e1c2cbd21687780153995f1be0c23,4661361,21253627,1,10.07,2017-09-01
1b9131d69fb9745f0c22e22c6d55437f,4656415,21229235,1,7.37,2017-09-01
03c9fd0e00e2cef5d72d0af8e869aabe,4658541,21239714,1,16.66,2017-09-01
8a31b963e8172ce71a0ef9549a0bd60a,4660567,21249687,1,5.03,2017-09-01
eef2ed08b1f18cab069ca4bf77015e27,4661588,21254705,3,7.41,2017-09-01
5b41bf39762066c0bdcd6db4bf8c3d3d,4658136,21237746,1,16.39,2017-09-01
30f581fb746101307867fe1c6c37d90b,4659813,21246099,1,33.61,2017-09-01
90735c44d307fd8bdc36effd46b54698,4660797,21250871,1,12.49,2017-09-01
123456789012345678901234567890ab,4658747,21240860,1,13.450000000000001,2017-09-01
""".lstrip()


@pytest.fixture
def db():
    from lsrtt.db.connection import connect_db
    with connect_db(':memory:') as con:
        yield con


@pytest.fixture
def dbloader():
    def loader(db, table):
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


@pytest.fixture
def predicted_db(db, model):
    from lsrtt.db.load import load_orders
    from lsrtt.db.predict import predict_db

    f = io.StringIO(CSV)
    load_orders(db, f, now='2017-10-17')
    predict_db(db, model)

    return db


@pytest.fixture
def app(predicted_db):
    lsrtt.web.app.app.testing = True
    app = lsrtt.web.app.app.test_client()
    with lsrtt.web.app.app.app_context():
        lsrtt.web.app.app._database = predicted_db

    yield app
