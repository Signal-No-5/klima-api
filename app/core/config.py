import logging

from sqlmodel import SQLModel

from app.core.database import Database
from app.core.prefs import AuthSettings, DatabaseSettings, settings
from app.models.admin import AuditLog

_dbs = [AuditLog]
# --- Logging setup ---
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.ERROR))
logger = logging.getLogger("app")
logger.info("Starting preparing the configs")
# --- Load settings ---
auth_settings = AuthSettings()
db_settings = DatabaseSettings()

# --- Initialize Database ---
db_manager = Database(db_settings, SQLModel)
logger.info("Initializing the db")
# if (settings.purge.lower() == "true") and (settings.app_env == "development"):
#     logger.info("Deleting the db")
#     db_manager.drop_all()
# Optionally create tables once on startup
db_manager.create_all()
