# Techcombank Fraud Detection Pipeline

Enterprise-grade fraud detection and risk intelligence for **Techcombank** — Vietnam’s leading tech-forward bank — on **T24** core banking, **AWS** (S3, streaming), **Databricks**/ML scoring patterns, and a continuously evolving fraud platform with international risk & data science experts.

## Architecture

```mermaid
graph TB
    T24["🏦 T24 Core Banking<br/>System<br/>GL • Contracts • Customers<br/>Transactions • Accounts"]
    
    T24 --> EXTRACT["📥 Extraction Layer<br/>API + CDC Streams<br/>GL Balances • Transactions<br/>Customer Profiles"]
    
    EXTRACT --> S3["☁️ S3 Raw Zone<br/>Bronze Layer<br/>Partitioned by Date/Account"]
    
    S3 --> VALIDATE["✅ Validation Stage<br/>Schema Check<br/>Duplicate Detection<br/>Data Quality Rules"]
    
    VALIDATE --> TRANSFORM["🔄 Silver Layer<br/>Data Enrichment<br/>Feature Engineering<br/>Risk Indicators<br/>Customer Profiles"]
    
    TRANSFORM --> GOLD["✨ Gold Layer<br/>Enriched Events<br/>Historical Snapshots<br/>ML Features"]
    
    GOLD --> RB["🎯 Rule-Based Detection<br/>Amount Threshold<br/>Velocity Check<br/>Location Anomaly<br/>Time Pattern"]
    
    GOLD --> ML["🤖 ML Anomaly Detection<br/>Isolation Forest<br/>XGBoost Ranking<br/>Ensemble Scoring"]
    
    RB --> SCORE["📊 Risk Scoring<br/>Combine Signals<br/>Calculate Probability"]
    ML --> SCORE
    
    SCORE --> ALERT["🚨 Fraud Alerts<br/>Severity Classification<br/>Auto-escalation"]
    
    ALERT --> PG["💾 PostgreSQL<br/>Alert History<br/>Case Management"]
    
    SCORE --> DASH["📈 Streamlit Dashboard<br/>Real-time Monitoring<br/>Risk Analytics<br/>Case Investigation"]
    
    ALERT --> COMPLIANCE["📋 Regulatory Reporting<br/>STR/CTR Generation<br/>Audit Trail"]
    
    AIRFLOW["⚙️ Airflow Orchestration"] -.-> EXTRACT
    AIRFLOW -.-> VALIDATE
    AIRFLOW -.-> TRANSFORM
    AIRFLOW -.-> SCORE
    
    style T24 fill:#1a5490,stroke:#000,color:#fff
    style EXTRACT fill:#3a7bd5,stroke:#000,color:#fff
    style S3 fill:#ff9900,stroke:#000,color:#fff
    style GOLD fill:#00b4d8,stroke:#000,color:#fff
    style SCORE fill:#ff006e,stroke:#000,color:#fff
    style ALERT fill:#ff1744,stroke:#000,color:#fff
    style DASH fill:#76ff03,stroke:#000,color:#000
```

## Data Pipeline Stages

| Stage | Component | Data Source | Description |
|-------|-----------|-------------|-------------|
| **1. Extraction** | `src/integrations/t24_extractor.py` | T24 GL API | Real-time API + CDC streams of GL balances, transactions, contracts |
| **2. S3 Staging** | `src/jobs/bronze_ingest.py` | AWS S3 Raw | Partition by date/account ID, Parquet format |
| **3. Validation** | `src/etl/validator.py` | Bronze Zone | Schema validation, duplicate detection, data quality checks |
| **4. Transformation** | `src/jobs/silver_transform.py` | Silver Zone | Feature engineering, risk indicators, customer enrichment |
| **5. Gold Layer** | `src/jobs/gold_kpi.py` | Gold Zone | ML-ready features, historical snapshots, aggregations |
| **6. Risk Scoring** | `src/fraud/detector.py` | Gold Zone | Rule-based + ML anomaly scoring |
| **7. Alerting** | `src/fraud/rules.py` | PostgreSQL | Fraud classification, escalation, regulatory flags |
| **8. Reporting** | `src/monitoring/dashboard.py` | Streamlit | Real-time dashboards, case investigation, compliance reports |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Source System** | T24 Core Banking (GL, Contracts, Customer Accounts) |
| **Data Lake** | AWS S3 (Bronze/Silver/Gold) + Redshift/RDS |
| **Language** | Python 3.10+ (Async, Multiprocessing) |
| **Data Processing** | PySpark, Pandas, DuckDB |
| **ML/Fraud Detection** | Scikit-learn, XGBoost, Isolation Forest |
| **Orchestration** | Apache Airflow 2.7+ |
| **Monitoring** | Streamlit, Plotly, Prometheus |
| **Logging** | Structlog (JSON), CloudWatch |
| **Configuration** | Pydantic, .env |
| **CLI** | Click with multi-command interface |
| **Containerization** | Docker, Docker Compose, Kubernetes |
| **CI/CD** | GitHub Actions (lint, test, deploy) |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure T24 connection
cp .env.example .env
# Edit .env: T24_API_URL, T24_API_KEY, AWS credentials

# 3. Run extraction pipeline (T24 → S3)
python -m src.jobs.bronze_ingest --date 2024-05-13 --incremental

# 4. Run transformation (Silver/Gold layers)
python -m src.jobs.silver_transform
python -m src.jobs.gold_kpi

# 5. Run fraud detection
python -m src.fraud.detector

# 6. Or use Airflow DAG
airflow dags trigger banking_fraud_detection_pipeline

# 7. Launch dashboards
streamlit run src/monitoring/dashboard.py
```

## Data Models

### T24 Core Banking Integration

**Source**: T24 Core Banking (General Ledger, Contracts, Customer Accounts)

```
T24 GL Structure:
├── General Ledger (GL Accounts)
│   ├── Account Balances
│   ├── Transaction History
│   └── Post-dated Items
├── Customer (CIF)
│   ├── Customer Master Data
│   ├── Account Holders
│   └── Contact Information
├── Contracts
│   ├── Deposit Products
│   ├── Loan Products
│   └── Service Agreements
└── Deal (Transactions)
    ├── Funding
    ├── Withdrawals
    └── Inter-account Transfers
```

**Extracted Tables** (S3 Parquet):
- `t24_gl_balances` — Account balances from GL master file
- `t24_transactions` — Posted and unposted transaction records
- `t24_contracts` — Product contracts linked to customers
- `t24_customers` — Customer master data with KYC information

## Repository Structure

```
techcombank-fraud-detection-platform/
├── src/
│   ├── config/              # Configuration management (pydantic-settings)
│   ├── etl/                 # ETL processing layer
│   │   ├── processor.py     # Core ETL pipeline
│   │   └── enricher.py      # Data enrichment features
│   ├── fraud/               # Fraud detection engine
│   │   ├── detector.py      # Multi-layered detector (rules + ML)
│   │   └── rules.py         # Configurable rule engine
│   ├── models/              # Pydantic domain models
│   ├── monitoring/          # Streamlit dashboard
│   ├── data_generator.py    # Synthetic data generation
│   ├── logger.py            # Structured logging
│   └── main.py              # CLI entry point
├── dags/                    # Airflow DAG definitions
├── db/                      # Database schema
├── data/                    # Sample transaction data
├── tests/                   # Unit and integration tests
├── notebooks/               # Exploration notebooks
├── docker-compose.yml       # Docker services
├── pyproject.toml            # Project configuration
└── README.md                # This file
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `techcombank-pipeline generate <n>` | Generate n synthetic transactions |
| `techcombank-pipeline etl` | Run ETL processing pipeline |
| `techcombank-pipeline detect` | Execute fraud detection engine |
| `techcombank-pipeline dashboard` | Launch monitoring dashboard |
| `techcombank-pipeline run-all` | Run complete pipeline end-to-end |

## Fraud Detection Rules

| Rule | Type | Description | Default Threshold |
|------|------|-------------|-------------------|
| High Value Transaction | Amount Threshold | Flags transactions exceeding configured limit | $10,000 |
| Rapid Consecutive Tx | Velocity Check | Detects multiple fast transactions from same account | 3 in 5 min |
| High Velocity Account | Velocity Check | Flags accounts with unusual transaction frequency | 10/hour |
| ML Anomaly Detection | Isolation Forest | Unsupervised anomaly detection on amount + temporal features | 1% contamination |

## Data Quality

- **Input validation**: Pydantic models enforce schema and constraints
- **ETL filtering**: Only completed transactions processed
- **Null handling**: Comprehensive null checks across pipeline
- **Logging**: JSON-structured logs for observability
- **Monitoring**: Dashboard with data quality KPIs

## Deployment

### Docker
```bash
docker-compose up -d
```

### Airflow
```bash
# Initialize Airflow
airflow db init
# Copy DAG to Airflow DAGs folder
cp dags/etl_dag.py $AIRFLOW_HOME/dags/
```

## License

MIT — See LICENSE for details.

---

*Built by Will Tran — Senior Data Engineer*