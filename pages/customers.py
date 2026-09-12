import streamlit as st
from datetime import datetime, time, timedelta, date
import pandas as pd

from mongodb_config.config import get_db
from validators.phone_normalizer import normalize_phone
from utils.customer_filters import build_orders_query
from utils.customer_processing import build_customers
from validators.campaign_validators import name_validator, message_validator, sender_number_validator
from services.faraz_sms import FarazSMSProvider
sms = FarazSMSProvider()


db = get_db()
orders = db["orders"]
campaigns = db["campaigns"]
campaign_recipients = db["campaign_recipients"]


# ----- ----- SIDEBAR

st.sidebar.header("Customer Filter")
st.sidebar.text("Filters")

# # ----- DATE RANGE

selected_start_date_paid = st.sidebar.date_input(
    "Start Date Paid",
    value=date(2026, 7, 1),
)

if selected_start_date_paid:
    start_datetime = datetime.combine(
        selected_start_date_paid,
        time.min
    )

selected_end_date_paid = st.sidebar.date_input(
    "End Date Paid",
    value=date.today(),
)

if selected_end_date_paid:
    end_datetime = datetime.combine(
        selected_end_date_paid + timedelta(days=1),
        time.min
    )

# # ----- PRODUCT IDs
product_mapping = {}

products = orders.find(
    {},
    {
        "product_id": 1,
        "product_name": 1,
    }
)

for order in products:
    product_ids = order.get("product_id", [])
    product_names = order.get("product_name", [])

    for product_id, product_name in zip(
        product_ids,
        product_names
    ):
        product_mapping[product_name] = product_id


selected_product_names = st.sidebar.multiselect(
    "Products",
    sorted(product_mapping.keys())
)

selected_product_ids = [
    product_mapping[name]
    for name in selected_product_names
]
    
# # ----- DISCOUNT CODE
selected_discount_code = st.sidebar.multiselect(
    "Discount Code",
    orders.distinct("discount_code")
)

# # ----- TOTAL RANGE

selected_start_total = st.sidebar.number_input(
    "Start Total Amount",
    step=1
)

selected_end_total = st.sidebar.number_input(
    "End Total Amount",
    step=1
)


query = build_orders_query(
    start_date=(
        start_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        if selected_start_date_paid
        else None
    ),
    end_date=(
        end_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        if selected_end_date_paid
        else None
    ),
    product_ids=selected_product_ids,
    discount_codes=selected_discount_code,
    start_total=(
        selected_start_total
        if selected_start_total
        else None
    ),
    end_total=(
        selected_end_total
        if selected_end_total
        else None
    ),
)

# ----- ----- MAIN CONTENT

orders_data = list(orders.find(query))
st.subheader("Create Campaigns by Customer filters")

# ----- PANDAS CALCULATIONS

df = pd.DataFrame(orders_data)
invalid_phone_count = 0
customer_count = 0

if not df.empty:
    df["phone_normalized"] = df["phone"].apply(normalize_phone)

    df["date_paid_dt"] = pd.to_datetime(
        df["date_paid"],
        errors="coerce",
        utc=True
    )

    invalid_phone_count = df["phone_normalized"].isna().sum()

    customers_df = build_customers(df)

    customers_df = customers_df.rename(
        columns={
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "phone_normalized": "شماره تلفن",
            "order_count": "تعداد سفارش‌ها",
            "total_purchase": "مجموع مبلغ خرید",
            "last_purchase": "تاریخ آخرین خرید",
        }
    )

    customers_df = customers_df[
        [
            "تاریخ آخرین خرید",
            "مجموع مبلغ خرید",
            "تعداد سفارش‌ها",
            "شماره تلفن",
            "نام خانوادگی",
            "نام",
        ]
    ]

else:
    customers_df = pd.DataFrame()
    
customer_count = len(customers_df)


# ----- DATA PREVIEW

col_6_1, col_6_2, col_6_3 = st.columns(3)
with col_6_1:
    st.metric(
        "Order Count",
        value=len(list(orders_data))
    )
with col_6_2:
    st.metric(
        "Unique Customers",
        customer_count
    )
with col_6_3:
    st.metric(
        "Invalid Phone Numbers",
        invalid_phone_count
    )
    
st.dataframe(
    customers_df,
    width="stretch"
)


# ----- CAMPAIGN

with st.container(border=True):
    st.subheader("Add New Campaign")
    with st.form("add_campaign"):
        name = st.text_input(
            "Name",
            placeholder="Please enter campaign name"
        )
        message = st.text_area(
            "Message",
            placeholder="Please enter message"
        )
        sender_number = st.selectbox(
            "Sender Number",
            sms.get_lines(),
            placeholder="Please choose sender number"
        )
        form_submitted = st.form_submit_button(
            "Submit"
        )
    if form_submitted:
        errors = [
            error
            for error in [
                name_validator(name),
                message_validator(message),
                sender_number_validator(sender_number),
            ]
            if error
        ]

        if errors:
            for error in errors:
                st.error(error)
        else:
            campaign_doc = {
                "name": name.strip(),
                "message": message.strip(),
                "sender_number": sender_number,

                "status": "draft",

                "stats": {
                    "total": len(customers_df),
                    "success": 0,
                    "failed": 0,
                    "pending": len(customers_df),
                },

                "created_at": datetime.now(),
                "last_sent_at": None,
            }
            campaign_result = campaigns.insert_one(campaign_doc)
            
            campaign_id = campaign_result.inserted_id
            recipients = customers_df["شماره تلفن"].tolist()
            recipient_docs = [
                {
                    "campaign_id": campaign_id,
                    "phone": phone,
                    "status": "pending",
                    "attempts": [],
                    "sent_at": None,
                    "error": None,
                }
                for phone in recipients
            ]
            campaign_recipients.insert_many(recipient_docs)
            st.success("Campaign created successfully!")