🚀 Project Overview

This project demonstrates a real-world Data Engineering pipeline built on AWS Cloud that integrates Calendly (meeting scheduling data) and Marketing Spend data to generate business insights.

The goal is to track how effective different marketing campaigns are at generating Calendly bookings and to calculate Cost Per Booking (CPB), Daily Calls, and other metrics using an end-to-end automated pipeline.

🎯 Objective

To design and deploy a production-grade data pipeline that:

Ingests Calendly webhook JSON data into AWS S3.

Transforms the data with AWS Glue.

Stores & Analyzes it using Amazon Redshift Serverless.

Visualizes results interactively via Streamlit dashboard.

🧱 Architecture
🗺️ Data Flow
Calendly Webhook → AWS Lambda → S3 (Landing)
          ↓
     AWS Glue Jobs (ETL)
          ↓
  S3 Bronze → Silver → Gold
          ↓
   Amazon Redshift (Tables + Views)
          ↓
       Streamlit Dashboard

🔹 Layers
Layer	Purpose	Example Output
Landing (S3)	Raw JSON webhook data	event, payload.email, payload.name
Bronze (S3)	Raw copied data backup	Unprocessed JSON
Silver (S3)	Flattened structured data	event, invitee_email, invitee_name
Gold (S3/Redshift)	Aggregated analytical data	Bookings, CPB, Trends
Redshift	Central analytics layer	Tables + Views
Streamlit	Visualization UI	Charts, KPIs, Leaderboards
☁️ AWS Services Used
Service	Purpose
Amazon S3	Data Lake storage for landing/bronze/silver/gold layers
AWS Glue	Serverless ETL transformations (PySpark jobs)
Amazon Redshift Serverless	Data warehouse for analytics
AWS IAM	Secure permissions between Glue, Redshift & S3
Streamlit	Front-end dashboard for visualization
GitHub Actions (optional)	CI/CD pipeline automation
🧩 Step-by-Step Implementation
1️⃣ S3 Setup

Created a bucket:

marketing-calendly-project/
├── landing/
├── bronze/
├── silver/
├── gold/
├── spend/


Uploaded sample JSON data (Calendly webhook) to landing/.

2️⃣ AWS Glue ETL Jobs
🪶 glue_bronze_job.py

Reads raw Calendly webhook JSON from landing/

Writes to bronze/ layer in S3

Used as a simple ingestion and raw copy backup

🧩 glue_silver_job.py

Reads from bronze/ layer

Flattens nested JSON (payload.email, payload.name)

Writes cleaned structured data to silver/ layer

🧠 (Optional) glue_gold_job.py

Joins Silver data with marketing spend data for advanced analytics

3️⃣ Amazon Redshift Setup

Created Serverless Workgroup: calendly-workgroup

Namespace: calendly-namespace

Made public for Streamlit access

SQL Scripts

redshift_tables.sql: Create tables for landing & spend

redshift_load_commands.sql: Load data from S3 to Redshift

redshift_views.sql: Create analytical views (Daily Calls, CPB)

✅ Example Tables:

CREATE TABLE IF NOT EXISTS landing (
    event VARCHAR(100),
    invitee_email VARCHAR(255),
    invitee_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS spend (
    event_type VARCHAR(100),
    total_spend DECIMAL(10,2)
);


✅ Example View:

CREATE OR REPLACE VIEW vw_cost_per_booking AS
SELECT
    l.event AS event_type,
    COUNT(l.invitee_email) AS total_invitees,
    COALESCE(s.total_spend, 0) AS total_spend,
    CASE WHEN COUNT(l.invitee_email) = 0 THEN 0
         ELSE COALESCE(s.total_spend, 0) / COUNT(l.invitee_email)
    END AS cost_per_booking
FROM landing l
LEFT JOIN spend s ON l.event = s.event_type
GROUP BY l.event, s.total_spend;

4️⃣ Streamlit Dashboard (Frontend Visualization)

📄 File: streamlit_app/app.py

Key Visualizations:

Metric	Visualization Type	Description
Daily Calls	Bar / Line Chart	Number of bookings per day
Cost Per Booking	Bar Chart	Spend ÷ Bookings per channel
Channel Summary	Table	Volume, Spend, CPB comparison

Example UI:

streamlit run streamlit_app/app.py


Then open:
👉 http://localhost:8501

5️⃣ Sample Data (Demo Files)

📁 sample_data/landing/landing_data.json

{
  "event": "invitee.created",
  "payload": {
    "email": "john.doe@example.com",
    "name": "John Doe"
  }
}


📁 sample_data/spend/spend_data_2025-06-24.json

[
  {"date": "2025-06-24", "channel": "facebook_paid_ads", "spend": 653.28},
  {"date": "2025-06-24", "channel": "youtube_paid_ads", "spend": 487.59},
  {"date": "2025-06-24", "channel": "tiktok_paid_ads", "spend": 345.12}
]

6️⃣ GitHub CI/CD Workflow (Optional)

📁 .github/workflows/deploy.yml

name: Validate Streamlit App

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: streamlit run streamlit_app/app.py --server.headless true

📊 Business KPIs Calculated
Metric	Formula	Description
Daily Calls	COUNT(bookings) per day	Monitor campaign performance
Cost Per Booking (CPB)	Spend / Bookings	Track marketing efficiency
Bookings Trend	COUNT by date	Detect growth patterns
Channel Attribution	CPB + total bookings	Rank channels by ROI
Meeting Load per Employee	COUNT / week	Identify resource utilization
📦 Folder Structure
aws-calendly-data-pipeline/
├── README.md
├── requirements.txt
├── architecture_diagram.png
│
├── streamlit_app/
│   ├── app.py
│   └── assets/
│       ├── logo.png
│       └── style.css
│
├── glue_jobs/
│   ├── glue_bronze_job.py
│   ├── glue_silver_job.py
│   └── glue_gold_job.py
│
├── redshift/
│   ├── redshift_tables.sql
│   ├── redshift_views.sql
│   ├── redshift_load_commands.sql
│   └── redshift_queries.sql
│
├── sample_data/
│   ├── landing/
│   │   └── landing_data.json
│   ├── spend/
│   │   ├── spend_data_2025-06-24.json
│   │   └── file_index.json
│   └── jsonpaths/
│       └── landing_jsonpaths.json
│
└── .github/
    └── workflows/
        └── deploy.yml

🧰 Requirements
streamlit==1.40.0
psycopg2-binary==2.9.9
pandas==2.2.3
boto3==1.35.15
awswrangler==3.10.0


Install dependencies:

pip install -r requirements.txt

📽️ Output Example
Metric	Screenshot
Daily Calls by Source	📊 Bar chart of bookings per campaign
Cost Per Booking	💰 Channel-wise CPB table

Channel Leaderboard	🏆 Sorted by bookings & spend
