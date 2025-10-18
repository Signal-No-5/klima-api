from fastapi import APIRouter
from sqlalchemy import Integer
from sqlmodel import func, select

from app.core.config import db_manager
from app.models.admin import AuditLog

router = APIRouter()


@router.get("/")
def root():
    return {"message": "🌦️ Klima API is running"}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/status")
async def status():
    async with db_manager.get_db() as db_sessions:
        session = next(iter(db_sessions.values()))  # first session
        counts = session.execute(
            select(
                func.sum((AuditLog.status_code >= 200) & (AuditLog.status_code <= 299))
                .cast(Integer)
                .label("2xx"),
                func.sum((AuditLog.status_code >= 400) & (AuditLog.status_code <= 499))
                .cast(Integer)
                .label("4xx"),
                func.sum((AuditLog.status_code >= 500) & (AuditLog.status_code <= 599))
                .cast(Integer)
                .label("5xx"),
            )
        )
        counts = counts.one()

    return {
        "stats": {
            "2xx": counts[0] or 0,
            "4xx": counts[1] or 0,
            "5xx": counts[2] or 0,
        }
    }
