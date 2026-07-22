from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ContactDB(Base):
    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)

    sentiment: Mapped[str] = mapped_column(String(50), default="unknown")
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    suggested_reply: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_available: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class MetricsDB(Base):
    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    total_contacts: Mapped[int] = mapped_column(Integer, default=0)
    ai_success_count: Mapped[int] = mapped_column(Integer, default=0)
    ai_fallback_count: Mapped[int] = mapped_column(Integer, default=0)
    sentiment_positive: Mapped[int] = mapped_column(Integer, default=0)
    sentiment_neutral: Mapped[int] = mapped_column(Integer, default=0)
    sentiment_negative: Mapped[int] = mapped_column(Integer, default=0)
    sentiment_unknown: Mapped[int] = mapped_column(Integer, default=0)


class RateLimitDB(Base):
    __tablename__ = "rate_limits"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    timestamps_json: Mapped[str] = mapped_column(Text, default="[]")
