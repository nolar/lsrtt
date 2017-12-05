import pkg_resources
from flask import Flask, current_app
from flask_restful import Resource, Api, abort

from lsrtt._defaults import DEFAULT_DB_PATH
from lsrtt.db.connection import connect_db

app = Flask(__name__)
api = Api(app, prefix='/api')


def get_db():
    # NB: sqlite3 objects are limited to the thread where they were created.
    # Thus, a connection per request. The path is set by `web.py` CLI (optionally).
    return connect_db(getattr(current_app, '_database_path', DEFAULT_DB_PATH))


@app.route('/')
def introduction():
    return pkg_resources.resource_string(__name__, 'introduction.html')


class Customers(Resource):
    def get(self):
        with get_db() as db:
            c = db.cursor()
            c.execute(""" select * from customers_agg """)
            result = [
                row['customer_id'] for row in c.fetchall()
            ]
            return result


class Predictions(Resource):
    def get(self, customer_id):
        with get_db() as db:
            c = db.cursor()
            c.execute(""" select * from customers_agg where customer_id = ? """, [customer_id])
            rows = c.fetchall()
            if not rows:
                abort(404, message="Customer {} doesn't exist.".format(customer_id))
            else:
                return {
                    'customer_id': rows[0]['customer_id'],
                    'predicted_clv': rows[0]['predicted_clv'],
                }


api.add_resource(Customers, '/customers')
api.add_resource(Predictions, '/customers/<string:customer_id>/predictions')

if __name__ == '__main__':
    app.run(debug=True)
