from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    method: str = Field(default="GET")
    path: str = Field(...)
    host: str = Field(...)
    status_code: int = Field(...)
    duration: float = Field(...)
    user_id: Optional[int] = Field()
    created_at: datetime = Field(default_factory=datetime.now)
