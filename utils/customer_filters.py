def build_orders_query(
    start_date=None,
    end_date=None,
    product_ids=None,
    discount_codes=None,
    start_total=None,
    end_total=None,
):
    query = {}

    # DATE RANGE
    date_paid_query = {}

    if start_date:
        date_paid_query["$gte"] = start_date

    if end_date:
        date_paid_query["$lt"] = end_date

    if date_paid_query:
        query["date_paid"] = date_paid_query

    # PRODUCT IDs
    if product_ids:
        query["product_id"] = {
            "$in": product_ids
        }

    # DISCOUNT CODE
    if discount_codes:
        query["discount_code"] = {
            "$in": discount_codes
        }

    # TOTAL RANGE
    total_query = {}

    if start_total is not None:
        total_query["$gte"] = start_total

    if end_total is not None:
        total_query["$lte"] = end_total

    if total_query:
        query["total"] = total_query

    return query
