from __future__ import absolute_import


def refresh_db(db, now):
    c = db.cursor()

    # This table must be updated/re-created every day on schedule, to refresh all the fields
    # that depend on the "current date".
    c.execute("""
        update customers_agg
        set days_since_last_order = julianday(?) - last_order_day,
            longest_interval_now = ifnull(longest_interval,
                (select avg_interval from interval_avg) + (julianday(?) - last_order_day))
        ;
    """, [now, now])
