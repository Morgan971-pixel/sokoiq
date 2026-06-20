from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Brief(Base):
    __tablename__ = "briefs"

    id = Column(String, primary_key=True)
    ticker = Column(String, index=True)
    company_name = Column(String)
    recommendation = Column(String)
    confidence = Column(Float)
    thesis = Column(Text)
    generated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    raw_json = Column(Text)
