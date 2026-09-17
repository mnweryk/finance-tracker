from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseConfig:
    """Configuration required to read holdings from the database.

    Attributes:
        host: Database host address.
        port: Database port number.
        name: Database name.
    """
    host: str
    port: int
    name: str