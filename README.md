# Personal Financial Tracker

> 🚧 **Project under development**

Contenerized, personal financial tracking system.

1. **Fetch** Reads user input from Google Sheets (verify exemplary google sheet template: https://docs.google.com/spreadsheets/d/1LtMzKNZc16C07y1OEW2qmy-ai7sM-NIeKcGzZwdknyk)

2. **Process** Calculate wallet value. Wallet is divided into portfolios, which can have multiple assets of different types. Currently supported assets are: bonds, cash, crypto, gold and stock

3. **Store** Save data to PostgreSQL database. Application may be run with option to skip data to database. Visualization will be not available in this form.

4. **Visualize** Show financial data with historical records on designed Grafana dashbord

> Note:
> For current and planned architecture please check [class diagram](docs/architecture.md)



## Project Stack
- **Python 3.14+** — application logic and tests
- **Google Sheets API** — reads portfolio and asset data
- **PostgreSQL** — stores portfolio snapshots and historical data
- **Grafana** — visualizes financial data
- **Docker** - application is contenerized, it is optional, however highly recommended


## Setup Instructions

### Clone repository 

```bash
# Clone repository
git clone <repository-url>
```

### Prepare configuration file
Config file exists in `config/config.toml`. It is configured to run application inside docker container.

Fill up Google credentials and database options. 

**Obtain Google credentials**

Create Google Service Account, manage Google Sheet access and obtain credentials .json file. 

For more information on obtaining Google credentials, please visit Google documentation:
https://docs.cloud.google.com/iam/docs/service-accounts-create and https://docs.cloud.google.com/iam/docs/keys-create-delete


**Database preparation**

Fill in database configuration (PostgreSQL is currently supported driver)  in `config/config.toml`. 

### Secrets preparation

Prepare `.secrets/` directory. It should contain files: `google_credentials.json` (file can be optionally in different location - alligned with config file), `grafana.env`, `postgres.env`

postgres.env content
```env
POSTGRES_USER=<user>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=<db_name>
POSTGRES_PORT=<port>
```

grafana.env content
```env
GF_SECURITY_ADMIN_USER=<user>
GF_SECURITY_ADMIN_PASSWORD=<password>
```

### Run application in Docker container

Application is designed to  be run inside docker container. To start PostgreSQL, grafana and application use docker-compose

1. Start containers inside docker directory
```sh
docker compose up -d
```
Finance-tracker all will gather data every 12h. If you want to modify this interval use INTERVAL env. Such configuration will proceed in data gathering every 12h:
```sh
INTERVAL=120 docker compose up -d
```

## Application Tests
To run unit tests, run command:
```bash
python tests/run_tests.py
```


