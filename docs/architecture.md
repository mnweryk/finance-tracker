```mermaid
classDiagram

    %% Domain Models
    class Wallet {
        +portfolios: list~Portfolio~
        +add_portfolio(portfolio_name: str)
        +get_portfolios(): list~Portfolio~
        +add_asset_to_portfolio(portfolio_name: str, holding: Asset)
        +get_total_value_pln(): Decimal
        +get_wallet_by_asset_type(): dict
    }

    class Portfolio {
        +name: str
        +assets: list~Asset~
        +add_asset(asset: Asset)
        +get_total_value_pln(): Decimal
        +portfolio_summary(): str
    }

    class Asset {
        <<abstract>>
        +name: str
        +ticker: Optional~str~
        +quantity: Decimal
        +currency: str
        +asset_type: str
        +unit_price_in_currency: Decimal
        +total_value_pln: Decimal
    }

    class Cash
    class Stock
    class Bond
    class Gold
    class Crypto

    class AssetFactory {
        -_ASSET_TYPES: dict
        +create(asset_type: str, name: str, currency: str, quantity: Decimal, ticker: Optional~str~): Asset
    }

    Asset <|-- Cash
    Asset <|-- Stock
    Asset <|-- Bond
    Asset <|-- Gold
    Asset <|-- Crypto
    AssetFactory ..> Cash : creates
    AssetFactory ..> Stock : creates
    AssetFactory ..> Bond : creates
    AssetFactory ..> Gold : creates
    AssetFactory ..> Crypto : creates

    %% Google Sheets Layer
    class GoogleSheetsConfig {
        +credentials_path: str
        +spreadsheet_id: str
        +worksheets: list~str~
    }

    class GoogleSheetsFetcher {
        -_spreadsheet
        +fetch_worksheet(worksheet_name: str): list~list~Any~~
        +fetch_worksheets(worksheet_names: list~str~): dict
    }

    class GoogleSheetsRowDTO {
        +asset_type: str
        +portfolio_name: str
        +name: str
        +quantity: Decimal
        +currency: str
        +ticker: Optional~str~
    }

    class GoogleSheetsHoldingParser {
        +config: GoogleSheetsConfig
        +spreadsheet_dto: list~GoogleSheetsRowDTO~
        +create_dtos(): list~GoogleSheetsRowDTO~
        +get_portfolios(raw_data: list): list~str~
        +parse_row(...): list~GoogleSheetsRowDTO~
    }

    GoogleSheetsFetcher --> GoogleSheetsConfig : uses
    GoogleSheetsHoldingParser --> GoogleSheetsConfig : uses
    GoogleSheetsHoldingParser ..> GoogleSheetsFetcher : fetches
    GoogleSheetsHoldingParser ..> GoogleSheetsRowDTO : creates

    %% Market Data Layer
    class MarketDataProvider {
        +get_stock_price(ticker: str): Decimal
        +get_currency_pln_rate(currency: str): Decimal
        +get_crypto_price(ticker: str): Decimal
        +get_gold_price_pln(): Decimal
        +convert_to_pln(func)
    }

    Asset ..> MarketDataProvider : gets prices and rates

    %% Orchestration
    class FinanceManager {
        -_config: GoogleSheetsConfig
        +wallet: Wallet
        +load_config(config_path: Path): GoogleSheetsConfig
        +load_sheets_data(): list~GoogleSheetsRowDTO~
        +build_wallet()
    }

    FinanceManager --> GoogleSheetsConfig : loads
    FinanceManager ..> GoogleSheetsHoldingParser : parses
    FinanceManager ..> GoogleSheetsRowDTO : consumes
    FinanceManager ..> AssetFactory : creates assets
    FinanceManager --> Wallet : builds
    FinanceManager ..> DatabaseConnection : opens session for snapshot save

    %% Domain relationships
    Wallet "1" *-- "*" Portfolio : contains
    Portfolio "1" *-- "*" Asset : contains

    %% Persistence Layer
    class DatabaseConfig {
        +host: str
        +port: int
        +name: str
    }

    class DatabaseConnection {
        +engine
        +SessionLocal
        +get_session(): Session
        +init_db()
    }

    class SnapshotRepository {
        -session: Session
        +get_or_create_wallet(wallet_name: str): WalletModel
        +save_snapshot(wallet: Wallet, snapshot_time: datetime): WalletSnapshotModel
    }

    class WalletModel {
        +id: int
        +name: str
    }

    class WalletSnapshotModel {
        +id: int
        +wallet_id: int
        +timestamp: datetime
    }

    class PortfolioSnapshotModel {
        +id: int
        +wallet_snapshot_id: int
        +name: str
    }

    class AssetSnapshotModel {
        +id: int
        +portfolio_snapshot_id: int
        +asset_type: str
        +name: str
        +ticker: Optional~str~
        +quantity: Decimal
        +currency: str
        +unit_price_in_currency: Decimal
        +total_value_pln: Decimal
    }

    DatabaseConnection --> DatabaseConfig : uses
    DatabaseConnection ..> WalletModel : creates schema
    SnapshotRepository --> WalletModel : gets or creates
    SnapshotRepository ..> WalletSnapshotModel : creates
    WalletModel "1" *-- "*" WalletSnapshotModel : has
    WalletSnapshotModel "1" *-- "*" PortfolioSnapshotModel : contains
    PortfolioSnapshotModel "1" *-- "*" AssetSnapshotModel : contains
    SnapshotRepository ..> Wallet : maps from domain
```

## Persistence and snapshot flow

The database layer is responsible for storing immutable, point-in-time views of the
domain wallet. It does not replace the domain models used to calculate values. The
mapping is one-way: `SnapshotRepository` reads the current `Wallet` aggregate and
creates a `WalletSnapshotModel` with nested `PortfolioSnapshotModel` and
`AssetSnapshotModel` records.

`DatabaseConnection` builds the SQLAlchemy engine from `DatabaseConfig`, creates the
database schema, and exposes a session context. The session context is the transaction
boundary: successful work is committed, an exception rolls the transaction back, and
the session is closed in either case. `SnapshotRepository` receives that session and
does not create its own connection.

The command-line flow is:

```mermaid
sequenceDiagram
    participant User
    participant Manager as FinanceManager
    participant Sheets as Google Sheets layer
    participant Domain as Wallet domain
    participant Connection as DatabaseConnection
    participant Session as SQLAlchemy Session
    participant Repo as SnapshotRepository
    participant DB as PostgreSQL

    User->>Manager: start application
    Manager->>Sheets: load and parse holdings
    Sheets-->>Manager: GoogleSheetsRowDTO list
    Manager->>Domain: create assets and portfolios
    Domain-->>Manager: populated Wallet
    Manager->>Connection: open get_session()
    Connection->>DB: create session
    Connection-->>Manager: Session
    Manager->>Repo: save_snapshot(wallet, session)
    Repo->>Session: get_or_create_wallet()
    Repo->>Session: add wallet snapshot graph
    Session->>DB: flush generated identifiers
    Repo-->>Manager: WalletSnapshotModel
    Manager-->>Connection: leave session context
    Connection->>DB: commit transaction
    Connection-->>User: snapshot saved
```

When `--skip_database_save` is supplied, the application still loads the holdings
and builds the in-memory wallet, but it does not create a database connection or
persist a snapshot.



