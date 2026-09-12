from config import get_db


db = get_db()

orders = db["orders"]
campaigns = db["campaigns"]
campaign_recipients = db["campaign_recipients"]


# =========================
# Orders
# =========================

orders.create_index(
    [("date_paid", 1)]
)

orders.create_index(
    [("product_id", 1)]
)

orders.create_index(
    [("discount_code", 1)]
)

orders.create_index(
    [("total", 1)]
)

orders.create_index(
    [("id", 1)],
    unique=True
)


# =========================
# Campaigns
# =========================

campaigns.create_index(
    [("status", 1), ("created_at", -1)]
)


# =========================
# Campaign Recipients
# =========================

campaign_recipients.create_index(
    [("campaign_id", 1), ("status", 1)]
)

campaign_recipients.create_index(
    [("campaign_id", 1), ("phone", 1)],
    unique=True
)


print("MongoDB indexes created successfully.")