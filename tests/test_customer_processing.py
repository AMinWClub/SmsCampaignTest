import pandas as pd

from utils.customer_processing import build_customers


def test_duplicate_customers_are_grouped():
    df = pd.DataFrame([
        {
            "phone_normalized": "09123456789",
            "first_name": "Amin",
            "last_name": "Test",
            "id": "OR001",
            "total": 100000,
            "date_paid_dt": pd.Timestamp("2026-07-01"),
        },
        {
            "phone_normalized": "09123456789",
            "first_name": "Amin",
            "last_name": "Test",
            "id": "OR002",
            "total": 200000,
            "date_paid_dt": pd.Timestamp("2026-07-10"),
        },
        {
            "phone_normalized": "09129876543",
            "first_name": "Ali",
            "last_name": "Test",
            "id": "OR003",
            "total": 300000,
            "date_paid_dt": pd.Timestamp("2026-07-05"),
        },
    ])

    result = build_customers(df)

    assert len(result) == 2


def test_duplicate_customer_order_count():
    df = pd.DataFrame([
        {
            "phone_normalized": "09123456789",
            "first_name": "Amin",
            "last_name": "Test",
            "id": "OR001",
            "total": 100000,
            "date_paid_dt": pd.Timestamp("2026-07-01"),
        },
        {
            "phone_normalized": "09123456789",
            "first_name": "Amin",
            "last_name": "Test",
            "id": "OR002",
            "total": 200000,
            "date_paid_dt": pd.Timestamp("2026-07-10"),
        },
    ])

    result = build_customers(df)

    assert len(result) == 1
    assert result.iloc[0]["order_count"] == 2
    assert result.iloc[0]["total_purchase"] == 300000
