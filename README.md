# Personal Financial Tracker

An automated financial tracking system that reads the current portfolio holdings from a Google Sheet, enriches them with current market prices (stocks, crypto, currencies), stores historical snapshots in database, and visualizes portfolio trends.

> 🚧 **Project under development**


## Project Architecture
> Note:
> For current and planned architecture please check [class diagram](docs/architecture.md)

1. **Fetch:** Read asset positions from Google Sheets (Read-Only via Service Account).
2. **Process:** Calculate asset values in base currency (PLN) using real-time market rates.
3. **Store:** Save daily time-series financial snapshots to PostgreSQL.
4. **Visualize:** Expose database tables to Grafana for portfolio historical analytics.

## Setup Instructions
**Prerequisites** 
1. Python 3.14+
2. Git

**Clone repository and install dependencies**

```bash
# Clone repository
git clone <repository-url>
cd finance-tracker

# Setup and activate virtual environment
python -m venv .venv

# On Linux / macOS / Git Bash:
source .venv/bin/activate

# On Windows (PowerShell):
# .venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

**Obtain Google credentials**
Create Google Service Account, manage Google Sheet access and obtain credentials .json file. 
Place it in `.secrets/credentials.json` or custom location that will be provided in configuration file

For more please visit Google documentation:
https://docs.cloud.google.com/iam/docs/service-accounts-create and https://docs.cloud.google.com/iam/docs/keys-create-delete

**Configure application**
To configure application, edit configuration file in [config/config.toml](config/config.toml)

**Run application and tests**
To run application, run command:
```bash
python src/finance_manager.py 
```

To run unit tests, run command:
```bash
python tests/run_tests.py
```


