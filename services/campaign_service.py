from datetime import datetime

from services.faraz_sms import FarazSMSProvider
from mongodb_config.config import get_db


db = get_db()

campaigns = db["campaigns"]
campaign_recipients = db["campaign_recipients"]


def send_campaign(campaign_id):

    # --------------------------------
    # Get campaign
    # --------------------------------

    campaign = campaigns.find_one({
        "_id": campaign_id
    })

    if not campaign:
        raise ValueError("Campaign not found.")

    # --------------------------------
    # Create SMS provider
    # --------------------------------

    provider = FarazSMSProvider()

    # --------------------------------
    # Get recipients that need sending
    # --------------------------------

    recipients = list(
        campaign_recipients.find({
            "campaign_id": campaign_id,
            "status": {
                "$in": ["pending", "failed"]
            }
        })
    )

    if not recipients:
        return {
            "success": True,
            "message": "No recipients to send.",
            "total": 0,
            "success_count": 0,
            "failed_count": 0,
            "pending_count": 0,
        }

    # --------------------------------
    # Mark campaign as sending
    # --------------------------------

    campaigns.update_one(
        {"_id": campaign_id},
        {
            "$set": {
                "status": "sending",
            }
        }
    )

    # --------------------------------
    # Send to recipients
    # --------------------------------

    for recipient in recipients:

        phone = recipient["phone"]

        attempt_number = (
            len(
                recipient.get("attempts", [])
            ) + 1
        )

        try:

            # ----------------------------
            # Send SMS
            # ----------------------------

            response = provider.send_message(
                recipients=[phone],
                message=campaign["message"],
                line_number=campaign["sender_number"],
            )

            # ----------------------------
            # SUCCESS
            # ----------------------------

            if response.get("success") is True:

                now = datetime.now()

                attempt = {
                    "attempt": attempt_number,
                    "status": "success",
                    "response": response,
                    "created_at": now,
                }

                campaign_recipients.update_one(
                    {"_id": recipient["_id"]},
                    {
                        "$set": {
                            "status": "success",
                            "sent_at": now,
                            "error": None,
                        },
                        "$push": {
                            "attempts": attempt,
                        },
                    }
                )

            # ----------------------------
            # PROVIDER RETURNED FAILURE
            # ----------------------------

            else:

                error_message = response.get(
                    "message",
                    "SMS sending failed."
                )

                attempt = {
                    "attempt": attempt_number,
                    "status": "failed",
                    "response": response,
                    "error": error_message,
                    "created_at": datetime.now(),
                }

                campaign_recipients.update_one(
                    {"_id": recipient["_id"]},
                    {
                        "$set": {
                            "status": "failed",
                            "sent_at": None,
                            "error": error_message,
                        },
                        "$push": {
                            "attempts": attempt,
                        },
                    }
                )

        # --------------------------------
        # EXCEPTION
        # --------------------------------

        except Exception as exc:

            error_message = str(exc)

            attempt = {
                "attempt": attempt_number,
                "status": "failed",
                "response": None,
                "error": error_message,
                "created_at": datetime.now(),
            }

            campaign_recipients.update_one(
                {"_id": recipient["_id"]},
                {
                    "$set": {
                        "status": "failed",
                        "sent_at": None,
                        "error": error_message,
                    },
                    "$push": {
                        "attempts": attempt,
                    },
                }
            )

    # --------------------------------
    # Calculate final statistics
    # --------------------------------

    total = campaign_recipients.count_documents({
        "campaign_id": campaign_id
    })

    success_count = campaign_recipients.count_documents({
        "campaign_id": campaign_id,
        "status": "success",
    })

    failed_count = campaign_recipients.count_documents({
        "campaign_id": campaign_id,
        "status": "failed",
    })

    pending_count = campaign_recipients.count_documents({
        "campaign_id": campaign_id,
        "status": "pending",
    })

    # --------------------------------
    # Determine campaign status
    # --------------------------------

    if success_count == total:
        campaign_status = "completed"
    else:
        campaign_status = "pending"

    # --------------------------------
    # Update campaign
    # --------------------------------

    campaigns.update_one(
        {"_id": campaign_id},
        {
            "$set": {
                "status": campaign_status,

                "stats": {
                    "total": total,
                    "success": success_count,
                    "failed": failed_count,
                    "pending": pending_count,
                },

                "last_sent_at": datetime.now(),
            }
        }
    )

    # --------------------------------
    # Return result to Streamlit
    # --------------------------------

    return {
        "success": True,
        "total": total,
        "success_count": success_count,
        "failed_count": failed_count,
        "pending_count": pending_count,
    }