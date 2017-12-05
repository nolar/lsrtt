from __future__ import absolute_import

import warnings

import dill
import numpy


def predict_db(db, model_path, predict_chunk_size=1):
    """ Execute the prediction on the customers and remember the results. """

    # FIXME: Workaround for buggy dill/dill-objects: requires the code dependencies in the main module, not locally.
    import __main__ as _main_module  # noqa
    _main_module.numpy = numpy

    with open(model_path, 'rb') as model_file:
        model = dill.load(model_file)

    # Retrieve all the customers for prediction. Should be done daily, as the predictions can change.
    c = db.cursor()
    c.execute("""
        select
            customer_id,
            max_items,
            max_revenue,
            all_revenue,
            num_orders,
            days_since_last_order,
            longest_interval_now
        from customers_agg
        where max_items is not null
          and max_revenue is not null
          and all_revenue is not null
          and num_orders is not null
          and days_since_last_order is not null
          and longest_interval_now is not null
    """)

    # Calculate the predictions in the chunks.
    # If the chunk has failed, ignore it, continue to the others.
    # TODO: on failure of a chunk, fall back to per-record prediction for that chunk.
    rows = c.fetchmany(predict_chunk_size)
    while rows:
        try:
            # Call the prediction model. Keep in mind, that it can fail for multiple reasons.
            ids = [row.customer_id for row in rows]
            arr = numpy.array([row[1:] for row in rows])
            res = model.predict(arr)
        except Exception as e:
            warnings.warn("Error while calculating the predicitons.", category=RuntimeWarning)
        else:
            # Store the predicted values and some logging info.
            c2 = db.cursor()
            c2.executemany("""
                update customers_agg
                set predicted_date = date(),
                    predicted_clv = ?
                where customer_id = ?
            """, zip(res, ids))
        finally:
            rows = c.fetchmany(predict_chunk_size)
