from __future__ import absolute_import

import csv


def dump_predictions(db, f, export_chunk_size=100):
    """ Dumps the predictions from the DB into the CSV file. """

    writer = csv.DictWriter(f, ['customer_id', 'predicted_clv'], delimiter=',')
    writer.writeheader()

    # Retrieve all the customers for prediction. Should be done daily, as the predictions can change.
    c = db.cursor()
    c.execute("""
        select
            customer_id,
            predicted_clv
        from customers_agg
    """)

    rows = c.fetchmany(export_chunk_size)
    while rows:
        try:
            writer.writerows(rows)
        finally:
            rows = c.fetchmany(export_chunk_size)
