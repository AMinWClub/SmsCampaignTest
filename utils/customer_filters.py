def build_orders_query(
    start_date=None,
    end_date=None,
    product_ids=None,
    discount_codes=None,
    start_total=None,
    end_total=None,
    date_product_operator="AND",
    date_discount_operator="AND",
    date_price_operator="AND",
):
    filters = []

    # DATE RANGE
    date_paid_query = {}

    if start_date:
        date_paid_query["$gte"] = start_date

    if end_date:
        date_paid_query["$lt"] = end_date

    date_filter = None

    if date_paid_query:
        date_filter = {
            "date_paid": date_paid_query
        }

    # PRODUCT
    product_filter = None

    if product_ids:
        product_filter = {
            "product_id": {
                "$in": product_ids
            }
        }

    # DISCOUNT
    discount_filter = None

    if discount_codes:
        discount_filter = {
            "discount_code": {
                "$in": discount_codes
            }
        }

    # PRICE / TOTAL
    total_query = {}

    if start_total is not None:
        total_query["$gte"] = start_total

    if end_total is not None:
        total_query["$lte"] = end_total

    total_filter = None

    if total_query:
        total_filter = {
            "total": total_query
        }

    # GROUPS
    and_filters = []
    or_filters = []

    # DATE
    if date_filter:
        or_filters.append(date_filter)

    # PRODUCT
    if product_filter:
        if date_filter and date_product_operator == "OR":
            or_filters.append(product_filter)
        else:
            and_filters.append(product_filter)

    # DISCOUNT
    if discount_filter:
        if date_filter and date_discount_operator == "OR":
            or_filters.append(discount_filter)
        else:
            and_filters.append(discount_filter)

    # PRICE
    if total_filter:
        if date_filter and date_price_operator == "OR":
            or_filters.append(total_filter)
        else:
            and_filters.append(total_filter)

    # Add OR group
    if or_filters:
        and_filters.append({
            "$or": or_filters
        })

    # Final query
    if not and_filters:
        return {}

    if len(and_filters) == 1:
        return and_filters[0]

    return {
        "$and": and_filters
    }