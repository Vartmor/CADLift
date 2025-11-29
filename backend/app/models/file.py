from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, DateTime, ForeignKey, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    job_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(32))
    storage_key: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(128))
    size_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job = relationship("Job", foreign_keys=[job_id])
    user = relationship("User")
