import io

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


# Yeah, yeah. I know. Not actually a unit test. I am just too tired already.
def test_full_cycle(db, dbloader, model):

    #
    # Loading stage
    #

    f = io.StringIO(CSV)

    from lsrtt.db.load import load_orders
    load_orders(db, f, now='2017-10-17')

    orders = dbloader('orders')
    orders_agg1 = dbloader('orders_agg1')
    orders_agg2 = dbloader('orders_agg2')
    orders_pks = {tuple(row[0:2]) for row in orders}
    orders_agg1_pks = {tuple(row[0:2]) for row in orders_agg1}
    orders_agg2_pks = {tuple(row[0:2]) for row in orders_agg2}

    assert len(orders) == 11
    assert len(orders_agg1) == 11
    assert len(orders_agg2) == 11
    assert orders_pks == orders_agg1_pks
    assert orders_pks == orders_agg2_pks
    assert len([True for row in orders if row.customer_id == CUSTOMER_ID]) == 2

    customers = dbloader('customers_agg')
    customer = [row for row in customers if row.customer_id == CUSTOMER_ID]
    assert len(customers) == 10
    assert len(customer) == 1

    #
    # Prediction stage
    #

    from lsrtt.db.predict import predict_db
    predict_db(db, model)

    customers = dbloader('customers_agg')
    customer = [row for row in customers if row.customer_id == CUSTOMER_ID]
    assert len(customers) == 10
    assert len(customer) == 1
    assert customer[0].predicted_clv == CUSTOMER_CLV  # just predicted

    #
    # Dumping stage
    #

    f = io.StringIO()

    from lsrtt.db.dump import dump_predictions
    dump_predictions(db, f)
    csv_text = f.getvalue()
    csv_lines = csv_text.splitlines()
    assert len(csv_lines) == 11
    assert csv_lines[0] == 'customer_id,predicted_clv'
    assert '{},{}'.format(CUSTOMER_ID, CUSTOMER_CLV) in csv_lines
