from __future__ import annotations

import importlib
import logging
import os
import sys
from typing import ClassVar, Dict, List, Literal, Union

from pydantic import Field, ValidationError, model_validator
from pydantic_settings import BaseSettings

from app.models.prefs import (
    DB_ENV_MAP,
    AnyAuthConfig,
    AnyDBConfig,
    Auth0Config,
    FirebaseConfig,
    KeycloakConfig,
    MSSQLConfig,
    MySQLConfig,
    OracleConfig,
    PostgresConfig,
    SocialConfig,
    SQLDialect,
    SQLiteConfig,
    SupabaseConfig,
)
from app.models.prefs.auth import SocialType
from app.models.prefs.db import DB_DRIVERS


class Settings(BaseSettings):
    app_env: str = Field(
        default="development",
        validation_alias="APP_MODE",
        description="Type of server to run",
    )
    app_port: int = Field(
        default=8000,
        validation_alias="APP_PORT",
        description="Port of which the server is taking",
    )
    secret_key: str = Field(
        default="",
        validation_alias="SECRET_KEY",
        description="Secret key for app's operations",
    )
    access_token_expire_minutes: int = Field(
        default=60,
        validation_alias="TOKEN_EXPIRETIME",
        description="Time it takes for tokens(JWTs) to expire",
    )
    log_level: Literal["INFO", "WARNING", "ERROR"] = Field(
        default="WARNING",
        validation_alias="LOG_LEVEL",
        description="The log level of the app",
    )
    purge: str = Field(
        default="FALSE",
        validation_alias="PURGE",
        description="Delete or not to delete the DB",
    )

    class Config:
        env_file = ".env"


settings = Settings()


class DatabaseSettings(BaseSettings):
    databases: Dict[str, AnyDBConfig] = Field(default_factory=dict)
    active_dialect: str = Field(
        default=os.getenv("DB_ACTIVE", "sqlite"),
        description="Active database dialect to use \
            (sqlite, postgres, mysql, mssql, oracle)",
    )
    db_log: ClassVar[logging.Logger] = logging.getLogger("app.database")

    @property
    def active_databases(self) -> List[AnyDBConfig]:
        result = [self.databases["sqlite"]]
        if self.active_dialect != "sqlite":
            db = self.databases.get(self.active_dialect)
            if not db:
                self.db_log.warning(
                    f"Active DB '{self.active_dialect}' not found, using SQLite only"
                )
            else:
                result.append(db)
        return result

    @model_validator(mode="before")
    def normalize_and_validate(cls, values: dict) -> Dict[str, AnyDBConfig]:
        cls.db_log.info("DB sqlite to be added onto the databases list")
        dbs: Dict[str, AnyDBConfig] = {}
        sqlite_file = os.getenv("SQLITE_FILE") or "klima-api.db"
        dbs["sqlite"] = SQLiteConfig(filename=sqlite_file)

        network_db_classes = {
            SQLDialect.POSTGRES: PostgresConfig,
            SQLDialect.MYSQL: MySQLConfig,
            SQLDialect.MSSQL: MSSQLConfig,
            SQLDialect.ORACLE: OracleConfig,
        }

        for dialect, cls_type in network_db_classes.items():
            env_map = DB_ENV_MAP[dialect]
            driver = DB_DRIVERS[dialect]
            if all(os.getenv(env_var) for env_var in env_map.values()):
                cls.db_log.info("DB %s to be added onto the databases list", dialect)
                try:
                    importlib.import_module(driver)
                except ModuleNotFoundError:
                    cls.db_log.error(
                        "DB driver %s for %s not installed", driver, dialect.value
                    )
                    continue
                db_config = cls_type(
                    host=os.getenv(env_map["host"]),
                    port=os.getenv(env_map["port"]),
                    name=os.getenv(env_map["name"]),
                    user=os.getenv(env_map["user"]),
                    password=os.getenv(env_map["password"]),
                )
                dbs[dialect.value] = db_config
        # Doesnt need the error, alr defaults to SQLite
        values["databases"] = dbs
        return values

    def get_url(self, dialect: str) -> str:
        """Returns the URL string for the given DB dialect."""
        if dialect not in self.databases:
            raise ValueError(f"Database '{dialect}' not configured")
        return self.databases[dialect].url


class AuthSettings(BaseSettings):
    providers: Dict[str, Union[AnyAuthConfig, Dict[str, SocialConfig]]] = Field(
        default_factory=dict
    )
    auth_log: ClassVar[logging.Logger] = logging.getLogger("app.auth")

    @classmethod
    def _validate_envs(cls, resource, **fields):
        """
        Validate that each provided field value is present (non-None).
        Returns a dict mapping key -> non-optional str for safe use afterwards.
        """
        validated: Dict[str, str] = {}
        for key, value in fields.items():
            if not value:
                cls.auth_log.error(f"Missing {resource.upper()}_{key.upper()}")
                sys.exit(1)
            validated[key] = value
        return validated

    @model_validator(mode="before")
    def validate_providers(cls, values):
        providers: Dict[str, Union[AnyAuthConfig, Dict[str, SocialConfig]]] = {}
        social_providers = {}

        for key, val in os.environ.items():
            if key.startswith("SOCIAL_") or key.endswith("_CLIENT_ID"):
                name = key.removeprefix("SOCIAL_").removesuffix("_CLIENT_ID").lower()

                # Validate enum name existence
                if name.upper() not in SocialType.__members__:
                    cls.auth_log.warning(
                        f"Unknown social provider '{name}' in env var '{key}'"
                    )
                    social_type_value = name  # Keep as string, fallback mode
                else:
                    social_type_value = SocialType[name.upper()]

                secret_key = f"SOCIAL_{name.upper()}_CLIENT_SECRET"
                secret = os.getenv(secret_key)
                validated = cls._validate_envs(
                    "social", client_id=val, client_secret=secret
                )

                try:
                    social_providers[name] = SocialConfig(
                        client_id=validated["client_id"],
                        client_secret=validated["client_secret"],
                        socialtype=social_type_value,
                    )
                except ValidationError as e:
                    cls.auth_log.error(f"Invalid config for {name}: {e}")
                    sys.exit(1)
        providers["social"] = social_providers

        if "KEYCLOAK_CLIENT_ID" in os.environ:
            client_id = os.getenv("KEYCLOAK_CLIENT_ID")
            client_secret = os.getenv("KEYCLOAK_CLIENT_SECRET")
            base_url = os.getenv("KEYCLOAK_BASE_URL")
            realm = os.getenv("KEYCLOAK_REALM")
            full_url = os.getenv("KEYCLOAK_FULL_URL")

            if not full_url and not (base_url and realm):
                cls.auth_log.error("full_url and base_url+realm not defined")
                sys.exit(1)

            validated = cls._validate_envs(
                "keycloak", client_id=client_id, client_secret=client_secret
            )

            try:
                if full_url:
                    providers["keycloak"] = KeycloakConfig(
                        client_id=validated["client_id"],
                        client_secret=validated["client_secret"],
                        full_url=full_url,
                    )
                elif base_url and realm:
                    providers["keycloak"] = KeycloakConfig(
                        client_id=validated["client_id"],
                        client_secret=validated["client_secret"],
                        base_url=base_url,
                        realm=realm,
                    )
            except ValidationError as e:
                cls.auth_log.error(f"Invalid Keycloak config: {e}")
                sys.exit(1)

        if "AUTH0_CLIENT_ID" in os.environ:
            client_id = os.getenv("AUTH0_CLIENT_ID")
            client_secret = os.getenv("AUTH0_CLIENT_SECRET")
            url = os.getenv("AUTH0_URL")
            validated = cls._validate_envs(
                "auth0", client_id=client_id, client_secret=client_secret, url=url
            )

            try:
                providers["auth0"] = Auth0Config(
                    client_id=validated["client_id"],
                    client_secret=validated["client_secret"],
                    url=validated["url"],
                )
            except ValidationError as e:
                cls.auth_log.error(f"Invalid Auth0 config: {e}")
                sys.exit(1)
        if "FIREBASE_PROJECT_ID" in os.environ:
            project_id = os.getenv("FIREBASE_PROJECT_ID")
            private_key = os.getenv("FIREBASE_PRIVATE_KEY")
            email = os.getenv("FIREBASE_CLIENT_EMAIL")
            validated = cls._validate_envs(
                "firebase",
                project_id=project_id,
                private_key=private_key,
                client_email=email,
            )
            try:
                providers["firebase"] = FirebaseConfig(
                    project_id=validated["FIREBASE_PROJECT_ID"],
                    private_key=validated["FIREBASE_PRIVATE_KEY"],
                    client_email=validated["FIREBASE_CLIENT_EMAIL"],
                )
            except ValidationError as e:
                cls.auth_log.error(f"Invalid Firebase config: {e}")
                sys.exit(1)

        # --- Handle SUPABASE ---
        if "SUPABASE_URL" in os.environ:
            client_id = os.getenv("SUPABASE_CLIENT_ID")
            client_secret = os.getenv("SUPABASE_CLIENT_SECRET")
            url = os.getenv("SUPABASE_URL")
            validated = cls._validate_envs(
                "supabase", client_id=client_id, client_secret=client_secret, url=url
            )

            try:
                providers["supabase"] = SupabaseConfig(
                    url=validated["url"],
                    client_secret=validated["client_secret"],
                )
            except ValidationError as e:
                cls.auth_log.error(f"Invalid Supabase config: {e}")
                sys.exit(1)
        if len(providers) == 0:
            cls.auth_log.warning("No auth providers configured")
        values["providers"] = providers
        return values
