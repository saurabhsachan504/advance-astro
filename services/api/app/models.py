from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class ForecastObservation(Base):
    __tablename__ = "forecast_observations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    profile_reference: Mapped[str] = mapped_column(String(128), index=True)
    prediction: Mapped[str] = mapped_column(Text)
    rule_key: Mapped[str] = mapped_column(String(160), index=True)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    contact_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="pending", index=True)
    outcome: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    feedback_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    followup_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class RuleFeedbackStat(Base):
    __tablename__ = "rule_feedback_stats"
    rule_key: Mapped[str] = mapped_column(String(160), primary_key=True)
    confirmed_count: Mapped[int] = mapped_column(Integer, default=0)
    declined_count: Mapped[int] = mapped_column(Integer, default=0)
    uncertain_count: Mapped[int] = mapped_column(Integer, default=0)
