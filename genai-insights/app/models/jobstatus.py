from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.db.base import Base


class JobStatus(Base):
    __tablename__ = "job_status"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String)
    status = Column(String)  # PENDING, RUNNING, COMPLETED, FAILED
    total = Column(Integer, default=0)
    processed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)