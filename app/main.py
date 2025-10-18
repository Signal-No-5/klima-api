from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import logger
from app.middleware.audit import AuditMiddleware
from app.routes import root

logger.info("Setting up the main API")

# Middlewares
app = FastAPI(title="Klima API")
app.add_middleware(AuditMiddleware)

# Routes
app.include_router(root.router, tags=["main"])

# Alerts
Instrumentator().instrument(app).expose(app)
