import uuid
from datetime import datetime, date

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import Base


def _uuid_column():
    """
    Helper to define a UUID primary key that works for both PostgreSQL and SQLite.
    """
    return Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class Conversion(Base):
    __tablename__ = "conversions"

    id = _uuid_column()
    raw_input = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tasks = relationship("Task", back_populates="conversion", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = _uuid_column()
    conversion_id = Column(UUID(as_uuid=True), ForeignKey("conversions.id"), nullable=False)
    task = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    priority = Column(String(50), nullable=False)
    deadline = Column(Date, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    conversion = relationship("Conversion", back_populates="tasks")

