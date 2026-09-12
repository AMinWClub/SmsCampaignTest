# SMS Campaign Management System

A Streamlit-based SMS Campaign Management System built with Python, MongoDB, PyMongo, Pandas, and the Faraz SMS API.

The application allows users to:

- Filter customers based on order data
- Normalize and validate Iranian mobile numbers
- Group multiple orders belonging to the same customer
- Create SMS campaigns
- Send campaigns through Faraz SMS
- Use a mock SMS provider for development and testing
- Retry failed recipients without sending messages again to successful recipients
- Track recipient-level sending attempts and results
- View campaign history
- Export campaign reports as CSV
- Run automated tests for core business logic

---

## Features

### Customer Filtering

Customers can be filtered based on:

- Paid date range
- Product
- Discount code
- Total purchase amount

The application queries MongoDB first and then processes the returned order data with Pandas.

Product names are displayed in the UI while the corresponding product IDs are used internally for MongoDB filtering.

---

### Customer Processing

Orders are converted into unique customers using their normalized phone numbers.

For each customer, the application calculates:

- First name
- Last name
- Number of orders
- Total purchase amount
- Last purchase date

Multiple orders belonging to the same phone number are grouped into a single customer.

Invalid phone numbers are excluded from the campaign recipient list and counted separately in the UI.

---

### Phone Number Normalization

Iranian mobile numbers are normalized before being used as campaign recipients.

Supported formats include:

```text
09123456789
989123456789
00989123456789
۰۹۱۲۳۴۵۶۷۸۹
0912-345-6789
```

All valid numbers are converted to the standard format:

```text
09123456789
```

Invalid phone numbers are ignored.

---

## Campaign Management

A campaign contains:

- Name
- Message
- Sender number
- Status
- Recipient statistics
- Creation time
- Last sending time

Campaign statuses include:

```text
draft
pending
sending
completed
```

A campaign starts as a draft and becomes pending/sending during the sending process.

A campaign is marked as completed only when all recipients have been successfully processed.

---

## Retry Logic

The system keeps recipient-level status independently.

Possible recipient statuses:

```text
pending
success
failed
```

When a campaign is sent:

- `pending` recipients are sent
- `failed` recipients are retried
- `success` recipients are skipped

This prevents successfully delivered messages from being sent again when a campaign is retried.

Each recipient also keeps an `attempts` array containing the history of previous sending attempts.

Example:

```json
{
  "phone": "09123456789",
  "status": "failed",
  "attempts": [
    {
      "attempt": 1,
      "status": "failed",
      "error": "Provider error"
    },
    {
      "attempt": 2,
      "status": "success"
    }
  ]
}
```

---

## SMS Provider

The application uses a dedicated `FarazSMSProvider` class to isolate SMS provider logic from the rest of the application.

The provider supports two modes:

```text
mock
live
```

### Mock Mode

Mock mode is the default and does not send real SMS messages.

Instead, the provider simulates successful and failed requests. This makes local development and testing possible without consuming SMS credit.

The mock provider randomly simulates successful and failed requests.

### Live Mode

Live mode sends requests to the Faraz SMS API.

The API key is loaded from an environment variable and is never hard-coded into the source code.

---

## Technology Stack

| Technology    | Purpose                      |
| ------------- | ---------------------------- |
| Python        | Main programming language    |
| Streamlit     | Web UI                       |
| MongoDB       | Database                     |
| PyMongo       | MongoDB driver               |
| Pandas        | Customer data processing     |
| Requests      | Faraz SMS API requests       |
| python-dotenv | Environment variable loading |
| Pytest        | Automated testing            |
| Mongomock     | MongoDB mocking during tests |

---

## Project Structure

```text
.
├── app.py
│
├── pages/
│   ├── customers.py
│   └── campaigns.py
│
├── services/
│   ├── campaign_service.py
│   └── faraz_sms.py
│
├── validators/
│   ├── campaign_validators.py
│   └── phone_normalizer.py
│
├── utils/
│   ├── customer_filters.py
│   └── customer_processing.py
│
├── mongodb_config/
│   ├── config.py
│   └── indexes.py
│
├── tests/
│   ├── test_campaign.py
│   ├── test_customer_filters.py
│   ├── test_customer_processing.py
│   └── test_phone.py
│
├── .env
├── pytest.ini
└── app.py
```

---

# Architecture

The project separates UI, business logic, validation, database configuration, and external API communication.

A simplified flow is:

```text
                    ┌──────────────────┐
                    │    Streamlit     │
                    │       UI         │
                    └────────┬─────────┘
                             │
               ┌─────────────┴─────────────┐
               │                           │
               ▼                           ▼
        Customers Page              Campaigns Page
               │                           │
               ▼                           ▼
      Customer Filters             Campaign Service
               │                           │
               ▼                           ▼
            MongoDB                 Faraz SMS Provider
               │                           │
               ▼                           ▼
           Pandas                    Faraz SMS API
```

---

## Customer Processing Flow

```text
MongoDB Orders
      │
      ▼
Build MongoDB Query
      │
      ▼
orders.find(query)
      │
      ▼
Normalize Phone Numbers
      │
      ▼
Parse Payment Dates
      │
      ▼
Group Orders by Phone
      │
      ▼
Unique Customers
      │
      ▼
Create Campaign Recipients
```

The database performs the initial filtering so unnecessary order records are not processed by Pandas.

---

## Campaign Sending Flow

```text
Campaign
   │
   ▼
Find pending/failed recipients
   │
   ▼
Send SMS
   │
   ├── Success
   │      └── recipient → success
   │
   └── Failure
          └── recipient → failed
   │
   ▼
Save attempt history
   │
   ▼
Recalculate statistics
   │
   ▼
Update campaign status
```

---

# Database

The application uses a MongoDB database named:

```text
sms_task
```

Collections:

```text
orders
campaigns
campaign_recipients
```

---

## Orders Collection

The `orders` collection contains customer order information.

Example:

```json
{
  "id": "OR0000117245",
  "first_name": "مشتری",
  "last_name": "آزمایشی",
  "phone": "09123456789",
  "date_paid": "2026-07-19T01:00:55.936514Z",
  "product_id": ["5811"],
  "product_name": ["Le Male Elixir"],
  "discount_code": "",
  "total": 3203000
}
```

---

## Campaigns Collection

A campaign document contains the campaign configuration and aggregated statistics.

Example:

```json
{
  "name": "Summer Campaign",
  "message": "Your campaign message...",
  "sender_number": "9000000",
  "status": "pending",
  "stats": {
    "total": 100,
    "success": 90,
    "failed": 10,
    "pending": 0
  },
  "created_at": "2026-07-20T10:00:00",
  "last_sent_at": null
}
```

---

## Campaign Recipients Collection

Each campaign recipient is stored separately.

Example:

```json
{
  "campaign_id": "ObjectId(...)",
  "phone": "09123456789",
  "status": "success",
  "attempts": [
    {
      "attempt": 1,
      "status": "success",
      "response": {},
      "created_at": "2026-07-20T10:05:00"
    }
  ],
  "sent_at": "2026-07-20T10:05:00",
  "error": null
}
```

This design makes it possible to track every recipient independently and retry only failed messages.

---

# MongoDB Indexes

The project creates indexes for frequently queried fields.

### Orders

```text
date_paid
product_id
discount_code
total
id (unique)
```

### Campaigns

```text
(status, created_at)
```

### Campaign Recipients

```text
(campaign_id, status)
(campaign_id, phone) UNIQUE
```

The indexes improve filtering performance and also prevent duplicate recipients from being created for the same campaign.

---

# Environment Variables

Create a `.env` file in the project root.

```env
MONGODB_CONNECTION_STRING=mongodb://localhost:27017

SMS_MODE=mock

FARAZSMS_API_KEY=
```

For local development, `mock` mode is recommended.

For real SMS sending:

```env
SMS_MODE=live
FARAZSMS_API_KEY=your_api_key
```

The API key is intentionally loaded from the environment instead of being stored in source code.

---

# Installation

Clone the project and enter the project directory.

Create a virtual environment:

```bash
python -m venv venv
```

Activate it.

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Make sure MongoDB is running locally.

Then configure the `.env` file.

---

# Database Index Setup

After configuring MongoDB, create the required indexes.

```bash
python mongodb_config/indexes.py
```

The script creates all required indexes for the application.

---

# Running the Application

Start Streamlit with:

```bash
streamlit run app.py
```

The application provides two main pages:

```text
Customers
Campaigns
```

---

# Customers Page

The Customers page allows filtering order data.

Available filters:

- Start Date Paid
- End Date Paid
- Product
- Discount Code
- Start Total Amount
- End Total Amount

After filtering, the application displays:

- Number of orders
- Number of unique customers
- Number of invalid phone numbers
- Customer data

A campaign can then be created from the resulting customer list.

---

# Campaign Creation

To create a campaign:

1. Filter customers.
2. Review the resulting customer list.
3. Enter a campaign name.
4. Enter the SMS message.
5. Select a sender number.
6. Submit the campaign.

Campaign validation checks:

- Campaign name is not empty.
- Campaign name contains at least 3 characters.
- Message is not empty.
- Message contains at least 15 characters.
- Sender number is not empty.

The campaign and its recipients are then stored in MongoDB.

---

# Sending Campaigns

From the Campaigns page, active campaigns can be sent.

The system:

1. Loads the campaign.
2. Finds recipients with `pending` or `failed` status.
3. Sends the SMS.
4. Stores the result of each attempt.
5. Updates recipient status.
6. Recalculates campaign statistics.
7. Updates the campaign status.

Successful recipients are not sent again during later retries.

---

# Campaign Reports

Each campaign provides a CSV report.

The report contains campaign-level and recipient-level information, including:

- Campaign name
- Campaign status
- Message
- Sender number
- Recipient phone number
- Recipient status
- Attempt number
- Attempt status
- Provider response
- Attempt error
- Sending timestamp
- Recipient sending timestamp
- Recipient error
- Campaign creation time
- Last campaign sending time

Multiple attempts for the same recipient are represented as separate rows so the complete sending history can be inspected.

---

# Testing

The project uses `pytest` for automated tests and `mongomock` for MongoDB-related testing.

Run all tests with:

```bash
pytest -v
```

The test suite covers the main business logic.

### Phone normalization

Tests include:

- Persian digits
- `98` prefix
- `0098` prefix
- Spaces and symbols
- Invalid numbers
- Empty values
- `None`

### Customer filtering

Tests cover:

- Product filtering
- Discount code filtering
- Combined filters
- Total amount ranges
- Date ranges

### Customer processing

Tests verify that:

- Duplicate customers are grouped.
- Order counts are calculated correctly.
- Total purchases are calculated correctly.

### Campaign sending

The campaign tests verify an important business rule:

> A successful recipient must never be sent again when a campaign is retried.

The test uses `mongomock` and a mocked SMS provider, so no real SMS is sent during testing.

---

# Test Configuration

The project contains a `pytest.ini` file:

```ini
[pytest]
pythonpath = .
```

This allows the test suite to import project packages such as:

```python
from services import campaign_service
from utils.customer_filters import build_orders_query
from validators.phone_normalizer import normalize_phone
```

---

# Development Mode

For development and testing, use:

```env
SMS_MODE=mock
```

This mode:

- Does not send real SMS messages.
- Does not require a real Faraz SMS API key.
- Simulates successful and failed provider responses.
- Makes it possible to test retry behavior safely.

Before enabling live mode, make sure the Faraz SMS credentials and sender line are correctly configured.

---

# Design Decisions

## Separation of Concerns

The project intentionally separates different responsibilities.

### `pages/`

Responsible for Streamlit UI and user interaction.

### `services/`

Responsible for business operations and external service communication.

### `validators/`

Responsible for input validation and phone normalization.

### `utils/`

Contains reusable customer filtering and processing logic.

### `mongodb_config/`

Contains MongoDB connection and index configuration.

### `tests/`

Contains automated tests for core business logic.

This structure keeps the Streamlit pages from containing all application logic in one place.

---

## Why Store Recipients Separately?

Campaign recipients are stored in a dedicated collection instead of embedding all recipients directly inside the campaign document.

This makes it possible to:

- Track each recipient independently.
- Store multiple sending attempts.
- Retry failed recipients.
- Query recipient status efficiently.
- Generate detailed reports.
- Prevent successful recipients from being resent.

---

## Why Use a Mock SMS Provider?

Sending real SMS messages during development is undesirable because it can:

- Consume SMS credit.
- Make automated testing unreliable.
- Depend on an external service.
- Produce real-world side effects.

The provider abstraction makes it possible to switch between:

```text
Mock Provider
       ↓
Local development / testing

Faraz SMS API
       ↓
Production
```

without changing the campaign business logic.

---

# Future Improvements

Possible improvements for a production-ready version include:

- Background job processing with Celery or another task queue
- Batch SMS sending instead of one request per recipient
- Campaign deletion with recipient cleanup
- Pagination for large customer and campaign datasets
- Authentication and authorization
- Better campaign locking/concurrency handling
- Provider webhook support for delivery status
- More detailed delivery statistics
- Scheduled campaigns
- Rate limiting
- Structured application logging
- Centralized error monitoring
- More comprehensive integration tests
- More efficient product mapping/querying for very large order datasets

---

# License

This project was created as a technical assignment / demonstration project.
