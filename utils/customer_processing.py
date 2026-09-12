def build_customers(df):
    if df.empty:
        return df

    customers_df = df.dropna(
        subset=["phone_normalized"]
    )

    customers_df = (
        customers_df
        .groupby("phone_normalized")
        .agg(
            first_name=("first_name", "first"),
            last_name=("last_name", "first"),
            order_count=("id", "count"),
            total_purchase=("total", "sum"),
            last_purchase=("date_paid_dt", "max"),
        )
        .reset_index()
    )

    return customers_df
