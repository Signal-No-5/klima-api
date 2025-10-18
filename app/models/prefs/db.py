from enum import Enum
from typing import ClassVar, Union

from pydantic import BaseModel, Field


class SQLDialect(str, Enum):
    SQLITE = "sqlite"
    POSTGRES = "postgres"
    MYSQL = "mysql"
    MSSQL = "mssql"
    ORACLE = "oracle"


DB_DRIVERS = {
    SQLDialect.POSTGRES: "asyncpg",
    SQLDialect.MYSQL: "aiomysql",
    SQLDialect.MSSQL: "pyodbc",
    SQLDialect.ORACLE: "cx_Oracle",
}

DB_ENV_MAP = {
    SQLDialect.POSTGRES: {
        "host": "POSTGRES_HOST",
        "port": "POSTGRES_PORT",
        "name": "POSTGRES_DB",
        "user": "POSTGRES_USER",
        "password": "POSTGRES_PASSWORD",
    },
    SQLDialect.MYSQL: {
        "host": "MYSQL_HOST",
        "port": "MYSQL_PORT",
        "name": "MYSQL_DB",
        "user": "MYSQL_USER",
        "password": "MYSQL_PASSWORD",
    },
    SQLDialect.MSSQL: {
        "host": "MSSQL_HOST",
        "port": "MSSQL_PORT",
        "name": "MSSQL_DB",
        "user": "MSSQL_USER",
        "password": "MSSQL_PASSWORD",
    },
    SQLDialect.ORACLE: {
        "host": "ORACLE_HOST",
        "port": "ORACLE_PORT",
        "name": "ORACLE_DB",
        "user": "ORACLE_USER",
        "password": "ORACLE_PASSWORD",
    },
}


class DBConfigBase(BaseModel):
    @property
    def url(self) -> str:
        raise NotImplementedError("Subclasses must implement url property")


class NetworkDBConfigBase(DBConfigBase):
    host: str = Field(..., description="DB host")
    port: str = Field(..., description="DB port")
    name: str = Field(..., description="DB name")
    user: str = Field(..., description="DB username")
    password: str = Field(..., description="DB password")


class SQLiteConfig(DBConfigBase):
    dialect: ClassVar[SQLDialect] = SQLDialect.SQLITE
    filename: str = Field(default="klima-api.db", description="SQLite file path")

    @property
    def url(self) -> str:
        return f"sqlite:///{self.filename}"


class PostgresConfig(NetworkDBConfigBase):
    dialect: ClassVar[SQLDialect] = SQLDialect.POSTGRES

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class MySQLConfig(NetworkDBConfigBase):
    dialect: ClassVar[SQLDialect] = SQLDialect.MYSQL

    @property
    def url(self) -> str:
        return f"mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class MSSQLConfig(NetworkDBConfigBase):
    dialect: ClassVar[SQLDialect] = SQLDialect.MSSQL

    @property
    def url(self) -> str:
        return f"mssql+pyodbc://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class OracleConfig(NetworkDBConfigBase):
    dialect: ClassVar[SQLDialect] = SQLDialect.ORACLE

    @property
    def url(self) -> str:
        return f"oracle+cx_oracle://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


AnyDBConfig = Union[
    SQLiteConfig, PostgresConfig, MySQLConfig, MSSQLConfig, OracleConfig
]
