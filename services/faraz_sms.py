
import os

import requests


class FarazSMSProvider:
    BASE_URL = "https://api.iranpayamak.com"

    def __init__(self):
        self.mode = os.getenv("SMS_MODE", "mock").lower()
        self.api_key = os.getenv("FARAZSMS_API_KEY")

        if self.mode not in {"mock", "live"}:
            raise ValueError("SMS_MODE must be either 'mock' or 'live'.")

        if self.mode == "live" and not self.api_key:
            raise ValueError("FARAZSMS_API_KEY is required in live mode.")

    def _headers(self):
        return {
            "Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def get_lines(self):
        """
        Return available sender lines.

        In mock mode no real API request is made.
        """

        if self.mode == "mock":
            return [
                '9000000', '2100000'
            ]

        response = requests.get(
            f"{self.BASE_URL}/ws/v1/lines/accessible",
            headers=self._headers(),
            timeout=10,
        )

        response.raise_for_status()
        return response.json()

    def send_message(
        self,
        recipients: list[str],
        message: str,
        line_number: str,
    ):
        """
        Send an SMS message.

        In mock mode the SMS is not actually sent.
        """

        if not recipients:
            raise ValueError("Recipients cannot be empty.")

        if not message.strip():
            raise ValueError("Message cannot be empty.")

        if not line_number.strip():
            raise ValueError("Line number cannot be empty.")

        if self.mode == "mock":
            import random
            is_success = random.random() < 0.7

            if is_success:
                return {
                    "success": True,
                    "mode": "mock",
                    "message": "SMS sent successfully.",
                    "recipients": recipients,
                    "message_text": message,
                    "line_number": line_number,
                    "message_id": f"mock-{random.randint(100000, 999999)}",
                }

            return {
                "success": False,
                "mode": "mock",
                "message": "SMS sending failed.",
                "recipients": recipients,
                "message_text": message,
                "line_number": line_number,
                "error": {
                    "code": random.choice([
                        "INVALID_RECIPIENT",
                        "INSUFFICIENT_CREDIT",
                        "PROVIDER_ERROR",
                        "TIMEOUT",
                    ]),
                    "description": "Simulated provider error.",
                },
            }

        payload = {
            "text": message,
            "line_number": line_number,
            "recipients": recipients,
            "number_format": "english",
            "schedule": None,
        }

        response = requests.post(
            f"{self.BASE_URL}/ws/v1/sms/simple",
            headers=self._headers(),
            json=payload,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()
