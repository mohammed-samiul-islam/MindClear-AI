import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import relationship

from .database import Base


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _uuid_column():
    """UUID primary key that works on both PostgreSQL (native uuid) and SQLite."""
    return Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)


class Conversion(Base):
    __tablename__ = "conversions"

    id = _uuid_column()
    session_id = Column(String(64), nullable=False, index=True)
    raw_input = Column(Text, nullable=False)
    source = Column(String(20), nullable=False, default="rules")
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    tasks = relationship("Task", back_populates="conversion", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = _uuid_column()
    session_id = Column(String(64), nullable=False, index=True)
    conversion_id = Column(Uuid(as_uuid=True), ForeignKey("conversions.id"), nullable=False)
    task = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    priority = Column(String(50), nullable=False)
    deadline = Column(Date, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    conversion = relationship("Conversion", back_populates="tasks")
