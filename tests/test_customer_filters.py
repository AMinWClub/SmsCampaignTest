from utils.customer_filters import build_orders_query


def test_filter_by_product():
    query = build_orders_query(
        product_ids=["5811", "5812"]
    )

    assert query == {
        "product_id": {
            "$in": ["5811", "5812"]
        }
    }


def test_filter_by_discount_code():
    query = build_orders_query(
        discount_codes=["SUMMER", "VIP"]
    )

    assert query == {
        "discount_code": {
            "$in": ["SUMMER", "VIP"]
        }
    }


def test_product_and_discount_filters_together():
    query = build_orders_query(
        product_ids=["5811"],
        discount_codes=["VIP"]
    )

    assert query == {
        "product_id": {
            "$in": ["5811"]
        },
        "discount_code": {
            "$in": ["VIP"]
        },
    }


def test_total_range_filter():
    query = build_orders_query(
        start_total=1000000,
        end_total=5000000,
    )

    assert query == {
        "total": {
            "$gte": 1000000,
            "$lte": 5000000,
        }
    }


def test_date_range_filter():
    query = build_orders_query(
        start_date="2026-07-01T00:00:00.000000Z",
        end_date="2026-08-01T00:00:00.000000Z",
    )

    assert query == {
        "date_paid": {
            "$gte": "2026-07-01T00:00:00.000000Z",
            "$lt": "2026-08-01T00:00:00.000000Z",
        }
    }