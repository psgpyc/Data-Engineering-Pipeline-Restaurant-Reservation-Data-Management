
# Ozzy: Multi-Platform Restaurant Booking Pipeline

This project showcases an end-to-end **automated data engineering pipeline** for a group of 10 restaurants using 4 different booking platforms.

As a data engineer, I’ve built a **production-grade architecture** that programmatically fetches booking data daily, stores and processes it using AWS and Python, and loads it into Snowflake for analytics and dashboarding.

---

## 🔧 Tools & Technologies

| Layer | Tools Used |
|-------|------------|
| **Infrastructure as Code(IaC)** | Terraform ( to provision S3, IAM setup) |
| **Cloud Provider** | AWS (Using Boto3) |
| **Data Processing** | SQL, Pandas |
| **Data Orchestration** | Apache Airflow |
| **Data Warehouse** | Snowflake (Python Connector / Snowpark) |
| **Visualization** | Tableau |
| **Monitoring/Alerting** | Logging, Email/Slack Alerts |
| **Project Automation** | GitHub Actions |
---

## 📦 Project Workflow

1. **Infrastructure Provisioning**  
   Provision 3 versioned S3 buckets (`raw`, `staging`, `processed`) and IAM roles using **Terraform**.

2. **Daily Data Extraction**  
   Python scripts query booking data from:
   - OpenTable API
   - TheFork API
   - Quandoo API
   - POS API

3. **Raw Data Storage**  
   Store unprocessed booking data in AWS S3 → `raw/` bucket.

4. **Data Cleaning & Transformation**  
   Process raw JSON/CSV files using Pandas and upload cleaned output to S3 → `processed/` bucket.

5. **Load to Snowflake**  
   Use **Snowflake Python Connector** or **Snowpark** to load cleaned data from S3 into Snowflake tables.

6. **Orchestration**  
   Use **Apache Airflow** to schedule and automate the entire pipeline end-to-end.

7. **Analytics**  
   Build dashboards in Tableau connected directly to Snowflake.

---

## 📁 Project Structure

```bash
.
├── infra-terraform/            # All Terraform code for AWS infra
│   └── modules/
│       └── s3_bucket/
├── dags/                       # Airflow DAGs
├── scripts/                    # Python ETL scripts
├── notebooks/                  # EDA or dev notebooks
├── snowflake/                 # SQL scripts or Python Snowflake loaders
├── .gitignore
├── README.md
└── requirements.txt
```
---

## 👨‍💻 Author

**Paritosh Ghimire**  
_Data Engineer _  
🌐 [LinkedIn](https://www.linkedin.com/in/psgpyc/) •
---

