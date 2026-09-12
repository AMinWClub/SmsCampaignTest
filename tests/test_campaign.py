from datetime import datetime
from unittest.mock import patch

import mongomock
from bson import ObjectId

from services import campaign_service


def test_successful_recipient_is_not_sent_again():

    db = mongomock.MongoClient().db

    campaigns = db["campaigns"]
    campaign_recipients = db["campaign_recipients"]

    campaign_id = ObjectId()

    campaigns.insert_one({
        "_id": campaign_id,
        "name": "Test Campaign",
        "message": "Test message",
        "sender_number": "9000000",
        "status": "pending",
        "created_at": datetime.now(),
    })

    successful_phone = "09123456789"
    failed_phone = "09129876543"

    campaigns_recipients = [
        {
            "campaign_id": campaign_id,
            "phone": successful_phone,
            "status": "success",
            "attempts": [
                {
                    "attempt": 1,
                    "status": "success",
                }
            ],
            "sent_at": datetime.now(),
            "error": None,
        },
        {
            "campaign_id": campaign_id,
            "phone": failed_phone,
            "status": "failed",
            "attempts": [
                {
                    "attempt": 1,
                    "status": "failed",
                }
            ],
            "sent_at": None,
            "error": "Provider error",
        },
    ]

    campaign_recipients.insert_many(
        campaigns_recipients
    )

    sent_numbers = []

    class MockSMSProvider:

        def send_message(
            self,
            recipients,
            message,
            line_number,
        ):
            sent_numbers.extend(recipients)

            return {
                "success": True,
                "mode": "mock",
            }

    with patch.object(
        campaign_service,
        "campaigns",
        campaigns,
    ), patch.object(
        campaign_service,
        "campaign_recipients",
        campaign_recipients,
    ), patch.object(
        campaign_service,
        "FarazSMSProvider",
        MockSMSProvider,
    ):

        campaign_service.send_campaign(
            campaign_id
        )

    assert successful_phone not in sent_numbers
    assert failed_phone in sent_numbers
    assert sent_numbers == [failed_phone]
