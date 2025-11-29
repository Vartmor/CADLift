from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    job_type: Mapped[str] = mapped_column(String(32))
    mode: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="queued")
    params: Mapped[dict | None] = mapped_column(JSON, default=dict)
    error_code: Mapped[str | None] = mapped_column(String(64))
    error_message: Mapped[str | None] = mapped_column(String(255))
    input_file_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("files.id", ondelete="SET NULL", use_alter=True, name="fk_jobs_input_file_id"),
    )
    output_file_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("files.id", ondelete="SET NULL", use_alter=True, name="fk_jobs_output_file_id"),
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
