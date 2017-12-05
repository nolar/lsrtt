from __future__ import absolute_import

import csv

from ._chunks import ichunk
from .refresh import refresh_db

NA = 'NA'


def convert_to_db(db, f, now, convert_chunk_size=1):
    """ Convert the source CSV file object into an indexed and pre-aggregated database. """

    c = db.cursor()

    # TODO: convert customer_id to integers for more compact record & faster indexing,
    # TODO: but since there are 16 bytes, and sqlite's max int is 8 bytes, it should be 8+8 field.
    c.executescript("""
        drop table if exists orders;
        create table orders (
            customer_id varchar not null,
            order_id integer not null,
            order_item_id integer,
            num_items integer,
            revenue real,
            created_at_date date,
            created_julian integer
        );
    """)

    # Transfer all data to the db as is. But cast the anonymized data to nulls (more convenient for us).
    # Chunks allow the
    reader = csv.DictReader(f, delimiter=',')
    for chunk in ichunk(reader, convert_chunk_size):
        c.executemany("""
            insert into orders 
                   (customer_id, order_id, order_item_id, num_items, revenue, created_at_date, created_julian)
            values (          ?,        ?,             ?,         ?,       ?,               ?, julianday(?)  )
        """, [
            [row['customer_id'], row['order_id'], row['order_item_id'], row['num_items'], row['revenue'], row['created_at_date'], row['created_at_date']]
            for row in ({key: None if val == NA else val for key, val in row.items()} for row in chunk)
        ])

    # Indexes help us to aggregate (group-by/order-by/select/join) faster.
    c.executescript("""
        create index orders_pk on orders (customer_id, order_id);
    """)

    # Now, when the data are in a normal indexed db, we can aggregate them.
    # This is usually faster than implementing the same algorithms locally.

    # Aggregate the data on the orders level.
    c.executescript("""
        drop table if exists orders_agg1;
        create table orders_agg1 as
        select
            customer_id,
            order_id,
            sum(num_items) as sum_num_items,
            sum(revenue) as sum_revenue
        from orders
        group by customer_id, order_id
        ;
        create index orders_agg1_pk on orders_agg1 (customer_id, order_id);
    """)

    # NB: We assume that the order-ids are sequential within a single day for the purpose of ordering them
    # NB: chronologically -- in order to determine the number of days till the next order; specifically,
    # NB: for the detection of this "next". Without this assumption, it is unclear which order came first.
    # NB: In the real world, we usually have both date & time for ordering.
    c.executescript("""
        drop table if exists orders_agg2;
        create table orders_agg2 as
        select
            o1.customer_id as customer_id,
            o1.order_id as order_id,
            min(o2.created_julian) - o1.created_julian as days_till_next_order
        from orders o1
        left join orders o2 on (
            o1.customer_id = o2.customer_id and
            o1.order_id != o2.order_id and
            (o1.created_julian < o2.created_julian or
            (o1.created_julian = o2.created_julian and o1.order_id < o2.order_id))
        )
        group by o1.customer_id, o1.order_id
        ;
        create index orders_agg2_pk on orders_agg2 (customer_id, order_id);
    """)

    # Aggregate the data on the customers level.
    c.executescript("""
        drop table if exists customers_agg;
        create table customers_agg as
        select o.customer_id as customer_id,
               max(a1.sum_num_items) as max_items,
               max(a1.sum_revenue) as max_revenue,
               sum(a1.sum_revenue) as all_revenue,
               count(*) as num_orders,
               max(o.created_julian) as last_order_day,
               max(a2.days_till_next_order) as longest_interval,
               0 as days_since_last_order,
               0 as longest_interval_now
        from orders o
        left join orders_agg1 a1 on (a1.customer_id = o.customer_id and a1.order_id = o.order_id)
        left join orders_agg2 a2 on (a2.customer_id = o.customer_id and a2.order_id = o.order_id)
        group by o.customer_id
        ;
        create index customers_agg_pk on customers_agg (customer_id);
    """)

    # Keep the pre-calculated value as a 1x1 table; instead of calculating it on each request.
    # No indexes needed, as this table is faster and smaller with whole-table-reads.
    c.executescript("""
        drop table if exists interval_avg;
        create table interval_avg as
        select avg(longest_interval) as avg_interval
        from customers_agg
        ;
    """)

    # After every new db creation, make the same refresh as regularly done for the field depending on "now".
    refresh_db(db, now)
