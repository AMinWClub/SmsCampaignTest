import streamlit as st
import pandas as pd
from mongodb_config.config import get_db
from services.campaign_service import send_campaign

db = get_db()

campaigns = db["campaigns"]
campaign_recipients = db["campaign_recipients"]

campaign_recipients.create_index(
    [("campaign_id", 1), ("status", 1)]
)
campaign_recipients.create_index(
    [("campaign_id", 1), ("phone", 1)],
    unique=True
)

def create_campaign_report(campaign):
    campaign_id = campaign["_id"]

    recipients = list(
        campaign_recipients.find(
            {"campaign_id": campaign_id}
        )
    )

    rows = []

    for recipient in recipients:
        attempts = recipient.get("attempts", [])

        # اگر هیچ تلاشی وجود نداشت
        if not attempts:
            rows.append({
                "Campaign Name": campaign.get("name", ""),
                "Campaign Status": campaign.get("status", ""),
                "Message": campaign.get("message", ""),
                "Sender Number": campaign.get("sender_number", ""),
                "Phone": recipient.get("phone", ""),
                "Recipient Status": recipient.get("status", ""),
                "Attempt": None,
                "Attempt Status": None,
                "Attempt Response": None,
                "Attempt Error": None,
                "Attempt At": None,
                "Sent At": recipient.get("sent_at"),
                "Recipient Error": recipient.get("error", ""),
                "Campaign Created At": campaign.get("created_at"),
                "Campaign Last Sent At": campaign.get("last_sent_at"),
            })

        else:
            for attempt_number, attempt in enumerate(
                attempts,
                start=1
            ):
                rows.append({
                    "Campaign Name": campaign.get("name", ""),
                    "Campaign Status": campaign.get("status", ""),
                    "Message": campaign.get("message", ""),
                    "Sender Number": campaign.get("sender_number", ""),
                    "Phone": recipient.get("phone", ""),
                    "Recipient Status": recipient.get("status", ""),

                    "Attempt": attempt_number,
                    "Attempt Status": attempt.get("status", ""),
                    "Attempt Response": attempt.get("response", ""),
                    "Attempt Error": attempt.get("error", ""),
                    "Attempt At": attempt.get("created_at"),

                    "Sent At": recipient.get("sent_at"),
                    "Recipient Error": recipient.get("error", ""),

                    "Campaign Created At": campaign.get("created_at"),
                    "Campaign Last Sent At": campaign.get("last_sent_at"),
                })

    report_df = pd.DataFrame(rows)

    return report_df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )


# ----- GET ALL ONGOING CAMPAIGNS
campaigns_data = campaigns.find({
    "status": {
        "$in": ["draft", "pending"]
    }
})

st.subheader("Drafted & Ongoing Campaigns")

for doc in campaigns_data:

    with st.container(border=True):

        # Header
        col1, col2 = st.columns([4, 1])

        with col1:
            st.subheader(doc["name"])

        with col2:
            status = doc["status"]

            if status == "draft":
                st.info("Draft")
            elif status == "pending":
                st.warning("Pending")

        # Campaign information
        col2, col3 = st.columns(2)

        with col2:
            st.metric(
                "Sender",
                doc.get("sender_number", "-")
            )

        with col3:
            created_at = doc.get("created_at")

            if created_at:
                created_at = created_at.strftime("%Y-%m-%d %H:%M")

            st.metric(
                "Created At",
                created_at or "-"
            )

        # Message
        with st.expander("View Message"):
            st.write(doc.get("message", "-"))
            
        recipients = list(
            campaign_recipients.find({
                "campaign_id": doc["_id"]
            })
        )

        success_count = sum(
            1 for r in recipients
            if r["status"] == "success"
        )

        failed_count = sum(
            1 for r in recipients
            if r["status"] == "failed"
        )

        pending_count = sum(
            1 for r in recipients
            if r["status"] == "pending"
        )
        
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total recipients", len(recipients))

        with col2:
            st.metric("Success", success_count)

        with col3:
            st.metric("Failed", failed_count)

        # Actions
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                "Send Campaign",
                key=f"send_{doc['_id']}"
            ):
                try:

                    with st.spinner("Sending campaign..."):
                        result = send_campaign(doc["_id"])

                    success_count = result["success_count"]
                    failed_count = result["failed_count"]
                    pending_count = result["pending_count"]

                    if failed_count == 0 and pending_count == 0:

                        st.success(
                            f"Campaign completed successfully. "
                            f"Success: {success_count}"
                        )

                    elif success_count > 0:

                        st.warning(
                            f"Campaign partially completed. "
                            f"Success: {success_count} | "
                            f"Failed: {failed_count}"
                        )

                    else:

                        st.error(
                            f"Campaign failed. "
                            f"Failed: {failed_count}"
                        )

                    st.rerun()

                except Exception as exc:

                    st.error(
                        f"Failed to send campaign: {exc}"
                    )

        with col2:
            if st.button(
                "Delete",
                key=f"delete_{doc['_id']}"
            ):
                st.write("Delete campaign")
        
        with col3:
            report_csv = create_campaign_report(doc)

            st.download_button(
                label="Download CSV",
                data=report_csv,
                file_name=f"campaign_{doc['_id']}.csv",
                mime="text/csv",
                key=f"report_active_{doc['_id']}",
            )
        
st.divider()

st.subheader("Campaign History")

completed_campaigns = list(
    campaigns.find(
        {"status": "completed"}
    ).sort("created_at", -1)
)

if completed_campaigns:

    for campaign in completed_campaigns:
        stats = campaign.get("stats", {})

        col1, col2, col3, col4, col5 = st.columns(
            [3, 1, 1, 1, 1]
        )

        with col1:
            st.markdown(
                f"**{campaign.get('name', '')}**"
            )

            st.caption(
                f"Created: {campaign.get('created_at', '')}"
            )
            
            st.write("Campaign Message:")
            st.write(campaign.get("message"))

        with col2:
            st.metric(
                "Total",
                stats.get("total", 0)
            )

        with col3:
            st.metric(
                "Success",
                stats.get("success", 0)
            )

        with col4:
            st.metric(
                "Failed",
                stats.get("failed", 0)
            )

        with col5:
            report_csv = create_campaign_report(campaign)

            st.download_button(
                label="CSV",
                data=report_csv,
                file_name=f"campaign_{campaign['_id']}.csv",
                mime="text/csv",
                key=f"report_completed_{campaign['_id']}",
                use_container_width=True,
            )

        st.divider()

else:
    st.info("No completed campaigns yet.")