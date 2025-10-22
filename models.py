from sqlalchemy import Column, String, JSON, DateTime
from datetime import datetime
from database import Base

class StringRecord(Base):
    __tablename__ = "strings"

    id = Column(String, primary_key=True, index=True)  # SHA-256 hash as primary key
    value = Column(String, nullable=False)  # Original string value
    properties = Column(JSON, nullable=False)  # Analyzed properties stored as JSON
    created_at = Column(DateTime, default=datetime.utcnow)  # Timestamp of creation