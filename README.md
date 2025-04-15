
# Data Engineering Pipeline: Restaurant Reservation Data Management

This project demonstrates a full-scale data engineering pipeline built using industry-standard tools and practices.  
It collects daily reservation data for three restaurants from mock APIs simulating OpenTable and The Fork, processes and validates the data, and stores it in AWS S3. The data is then systematically loaded into a Snowflake data warehouse. The pipeline is fully automated using Apache Airflow and AWS services, with infrastructure provisioned using Terraform.

## Technology Stack

- **AWS Lambda & EventBridge Scheduler**: Serverless compute & automation.
- **AWS EC2 & FastAPI**: Simulated real-world API endpoints.
- **Terraform**: Infrastructure as Code (IaC) for AWS resource provisioning.
- **Apache Airflow**: Pipeline orchestration and automation.
- **Snowflake**: Cloud data warehouse solution.
- **AWS S3**: Data Lake storage.
- **Python & SQL**: Core programming language.
- **Pydantic**: Data validation and modeling.
- **Boto3**: Python SDK for AWS.
- **Snowflake Python Connector**: Connecting Python applications to Snowflake.

---

### Workflow
1. **Data Generation (AWS Lambda & Scheduler)**
   - **AWS Lambda** generates mock reservation data daily.
   - **AWS EventBridge Scheduler** automates the daily execution of Lambda.
   - Data is stored in an S3 raw bucket.

2. **API Simulation (FastAPI & EC2)**
   - An **EC2 instance** running FastAPI acts as a web server, simulating real-world API endpoints.
   - The API retrieves processed reservation data from S3 and serves it in JSON format.

3. **Data Processing & Validation (Python & Pydantic)**
   - Extracted data is validated using **Pydantic** models.
   - Unnecessary data is removed, and processed data is stored in a separate S3 staging bucket.

4. **Data Storage & Warehousing (AWS S3 & Snowflake)**
   - Processed data is loaded into **Snowflake** using the Snowflake Python connector.


### Infrastructure Provisioning
- Infrastructure, including EC2 instances, AWS Lambda functions, S3 buckets, IAM roles, and policies, are provisioned using **Terraform**.

### Pipeline Orchestration
- **Apache Airflow** orchestrates the entire ETL workflow, ensuring automated execution, monitoring, and error handling.
- Extended **logging** functionality enhances Airflow's default logs with custom messages for better traceability.



## Flowchart

### Infrastructure Provisioning Flowchart

```mermaid
graph TD;
    A[Terraform] --> B[Provision EC2 Instance];
    A --> C[Provision AWS Lambda & Scheduler];
    A --> D[Create S3 Buckets];
    A --> E[Set IAM Roles & Policies];
    B --> F[EC2 with FastAPI];
    C --> G[Lambda for Data Generation];
    D --> H[S3 Staging & Processed Buckets];
```

### Data Generation and Serving Flowchart

```mermaid
graph LR;
    A[AWS EventBridge <br>  Scheduler Invokes <br> AWS lambda] --> B[AWS Lambda Generates <br> Mock Data <br> daily];
    B --> C[Uploads to <br> S3 Staging Bucket];
    C --> D[FastAPI on EC2 Serves <br> JSON Data via API Endpoint];
```

### Data Pipeline Flowchart

```mermaid
graph LR;
    A[Daily Airflow Pipeline Triggred] --> B[Booking Platform API<br>Endpoint Hit] --> C[FastAPI on EC2<br>Handles Request];
```
```mermaid
graph TD
    C[Extract DAG <br> aggregates data <br> and passes to <br> Validation DAG] --> D[Data <br> Cleaning & Validation<br>with Pydantic];
    D --> E[S3 Processed<br>Data Storage];
    E --> F[Snowflake connects to External s3<br>Table Staging];
    F --> G[Pre-Load Checks<br>in Snowflake];
    G --> H[Final Load into<br>Snowflake Warehouse Table];
```

### Project Structure 

```bash
.
├── dags/                             # Main Airflow DAG project folder
│   ├── config/                       # settings & configuration
│   ├── loader/                       # Pre-load checks for Snowflake
│   ├── logs/                         # ETL run logs
│   ├── pipelines/                    # Extract, process, load scripts
│   ├── snowflakecore/                # Snowflake loaders SQL Scripts
│   ├── utils/                        # Helper functions (connections, checks)
│   ├── validators/                   # Data validation with Pydantic                 
│   └── pipeline.py                   # DAG orchestration entrypoint
├── endpoints/                       # FastAPI app for mock booking APIs
├── infrastructure/                  # Terraform AWS infra setup
│   └── modules/                     # Modular AWS resources (S3, Lambda, etc.)
├── requirements.txt                 # Python dependencies
└── README.md                        # Project overview


## 👨‍💻 Author

[Paritosh Sharma Ghimire](https://www.linkedin.com/in/psgpyc/)
---

