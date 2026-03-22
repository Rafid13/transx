## Assumptions:
### API:
- For purpose of this project it is assumed that rest API will only be used for reading data from the Database. It will not be used to update the database.
- The project in current state is considered as MVP/ PoC which will later be enhanced. It is good enough to deploy on Production as it only performs read-operations and does update the database.

### DB Seeding
- In Database seeding script it is assumed that payments will always be made in the Country of origin's currency.
- The dummy address list used in db_seed.py script is loosely constructed. The script does not have any checks to match the address with Country of transaction.

---

## Prerequisites

- Python (built on 3.11.0)
- MySQL (tested on latest version)
- pip 

---

## Installation

### Clone the repository

```pwsh
git clone https://github.com/Rafid13/transx.git
cd project
```

### Install dependencies

```pwsh
pip install -r requirements.txt
```

### Configure the database

Edit `config.yaml` with your MySQL connection details:

```yaml
database:
  host: localhost (or server name/ ip)
  port: 3306
  user: your_db_user
  password: your_db_password
  name: payments_db
```

---

> **Note:** The Rest API needs data in the database to function. For testing seed the database before running API.


## Seeding the Database
The `db_seed.py` script generates and inserts randomised transaction records into the database.

| Argument | Type | Description |
|---|---|---|
| `--tranx` | integer | Number of transactions to generate |
| `--start-date` | YYYY-MM-DD | Start of the random date range |
| `--end-date` | YYYY-MM-DD | End of the random date range |
| `--db-config` | file path | Path to config.yaml (default: `../config.yaml`) |

### Examples

**Seed 20,000 transactions:**
```pwsh
python db_seed.py --tranx 20000 --start-date 2.25-01-01 --end-date 2025-01-01
```

**Seed 500 transactions with a custom config path:**
```pwsh
python db_seed.py --tranx 500 --start-date 2023-06-01 --end-date 2.25-06-01 --db-config ./config.yaml
```

---

## Run the API

```pwsh
python app.py
```

The API will start on `http://localhost:5000`. 


## REST API Reference


All endpoints are HTTP `GET`. Base URL: `http://localhost:5000`

| Method | Endpoint | Query Params | Description |
|---|---|---|---|
| GET | `/transactions` | `days=n` | All transactions in the last n days |
| GET | `/transactions/count` | `days=n, card_type=xyz` | Count of transactions by card type in last n days. Valid values for card type are VISA, MASTERCARD and AMEX (case-sensitive) |
| GET | `/transactions/country` | `days=n, country=xyz` | Transactions by country of origin in last n days. Valid values for Countries are  |
| GET | `/transactions/amount` | `days=n, min_amount=123, max_amount=456` | Transactions within an amount range in last n days |

---

### GET /transactions

Returns all transactions made in the last n days.

**Query Parameters**
- `days` *(required)* — number of days to look back

**Example Request**
```
GET http://localhost:5000/transactions?days=30
```

**Example Response**
```json
[
  {
    "Id": "00004dd1-4204-4432-b58e-a79955d3dcc8",
    "Date": 1763597923012,
    "Amount": 243.92,
    "Currency": "CAD",
    "Vendor": "ServiceProvider-1",
    "CardType": "MASTERCARD"
  },
]
```

---

### GET /transactions/count

Returns the number of transactions for a given card type in the last n days.

**Query Parameters**
- `days` *(required)* — number of days to look back
- `card_type` *(required)* — one of: `visa`, `mastercard`, `amex` (case-insensitive)

**Example Request**
```
GET http://localhost:5000/transactions/count?days=30&card_type=VISA
```

**Example Response**
```json
{
  "days": 30,
  "card_type": "VISA",
  "count": 842
}
```

---

### GET /transactions/country

Returns all transactions from a specific country of origin in the last n days.

**Query Parameters**
- `days` *(required)* — number of days to look back
- `country` *(required)* — country code e.g. `UK`, `US`, `AUD`, `CAD`, `EUR`

**Example Request**
```
GET http://localhost:5000/transactions/country?days=60&country=UK
```

**Example Response**
```json
{
  "days": 300,
  "country_of_origin": "UK",
  "transactions": [
      {
        "Id": "003b431e-af6d-44a7-aaaa-1a16184a0877",
        "Date": 1765518183454,
        "Amount": 31.96,
        "Currency": "GBP",
        "Vendor": "Shop-2",
        "CardType": "MASTERCARD"
      },
      {
        "Id": "00673e40-7173-4090-b545-a88cf0e4fcba",
        "Date": 1764654759796,
        "Amount": 792.11,
        "Currency": "GBP",
        "Vendor": "Shop-2",
        "CardType": "MASTERCARD"
      },
      --------
    ]
}
```

---

### GET /transactions/amount

Returns all transactions where the amount falls within a specified range in the last n days.

**Query Parameters**
- `days` *(required)* — number of days to look back
- `min_amount` *(required)* — minimum transaction amount
- `max_amount` *(required)* — maximum transaction amount

**Example Request**
```
GET http://localhost:5000/transactions/amount?days=90&min_amount=100&max_amount=500
```

**Example Response**
```json
{
  "days": 90,
  "min_amount": 100.0,
  "max_amount": 500.0,
  "total_count": 170,
  "transactions": [
    {
      "Id": "00651e32-fc6e-4151-b24c-85dab13f2be7",
      "Date": 1766543000730,
      "Amount": 326.7,
      "Currency": "CAD",
      "Vendor": "ServiceProvider-1",
      "CardType": "VISA"
    },
    {
      "Id": "02bd897d-af5d-4588-8ba1-d83d493161f1",
      "Date": 1766858566344,
      "Amount": 195.09,
      "Currency": "CAD",
      "Vendor": "ServiceProvider-2",
      "CardType": "MASTERCARD"
    },
    -----
  ]
}
```

---

## Running Tests

Tests are located in the `tests/` directory and use Python's built-in `unittest` framework.

**Run all tests with verbose output:**
```pwsh
python -m unittest discover -s tests -v
```

**Generate an HTML test report:**
```pwsh
pytest tests/ -v --html=report.html --self-contained-html
```

This produces a `report.html` file in the project root that can be opened in any browser.

---

### AWS Deployment Considerations:

- The Rest API should be containerised and deployed to Cloud Platform for resilience.
- The database confguration in config.yaml will have to be moved AWS Secret manager. 
- The API code will have to be updated to read database connection details from AWS secret

## AWS Hosting

| Service | Purpose |
|---|---|
| **ECS (Fargate)** | Runs the Docker container — serverless, no EC2 instances to manage |
| **RDS (MySQL)** | Managed MySQL database — replaces local MySQL |
| **ALB** | Application Load Balancer — distributes traffic, handles SSL termination |
| **ECR** | Elastic Container Registry — stores Docker images |
| **Secrets Manager** | Stores database credentials securely at runtime |
| **CloudWatch** | Logs, metrics, and alerting |
| **WAF** | Web Application Firewall — production only |
| **VPC** | Isolates each environment's network |

> Use Terraform to build all of the above reliably and with easy reproducability.

## Multi-Environment Setup

- Each environment should be **fully isolated** — ideally separate AWS accounts, or at minimum separate VPCs. Each has its own ECS cluster, RDS instance, and ALB. The same infrastructure code is reused across environments, with different variable values for instance sizes and replica counts.

- Non-prod sku sizes for RDS, ECS etc should be small where Production could be large or medium depending on expected usage. 

## CI/CD Pipeline
- The API and IaC code should be deployed using pipeline with tools like Jenkins, GitHub Actions or Azure DevOps. 
- GitOps based approach could be use to automatically run the pipeline when pushes are made to certain branches. for e.g. dev pipeline to trigger when a commit is made to any branch under develop/, test pipeline to trigger when a commit is made to any branch under release/ and prod pipeline is ran when any new commit is made to main. 
- Prod environment should have an approval gate. 

## Basic pipeline structure 

```
Developer pushes code to develop/dev1 branch
        │
        ▼
   Run tests (pytest)
        │
     Pass? ──No──► Block merge, notify developer
        │
       Yes
        ▼
   Run SAST 
        │
     Pass? ──No──► Block merge, notify developer
        │
       Yes
        ▼
   Build Docker image
        │
        ▼
   Run DAST 
        │
     Pass? ──No──► Block merge, notify developer
        │
       Yes
        ▼
   Push to ECR 
        │
        ▼
   Deploy to Dev 
        │
   Merge changes from develop/dev1 to release/r1
        ▼
   Deploy to Test (automatic)
        │
        ▼
   Merge changes from  release/r1 to main (post UAT)
        |    
    Pass? ──No──► Block merge, notify developer
        │
       Yes
        ▼   
   Deploy to Production (manual approval gate)
```
