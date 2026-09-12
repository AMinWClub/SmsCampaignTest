import streamlit as st

customers_page = st.Page(
    "pages/customers.py",
    title="Customers",
    icon="👥",
)
campaigns_page = st.Page(
    "pages/campaigns.py",
    title="Campaigns",
    icon="🚩",
)


pg = st.navigation([
    customers_page,
    campaigns_page
])
pg.run()