from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    func
)

from app.db.base import Base


class SearchConfig(Base):
    __tablename__ = "searchconfig"

    # Primary Key
    search_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Core Fields
    source = Column(String(100), nullable=True)          # flipkart, amazon
    product = Column(String(255), nullable=True)         # Moto Edge 60 Pro
    url = Column(Text, nullable=True)
    sourcefilename = Column(String(255), nullable=False)

    # Control Flags
    enabled = Column(Integer, nullable=False, default=1)  # behaves like boolean
    lastrowno = Column(Integer, nullable=True)

    # Metadata
    country = Column(String(50), nullable=True)

    # Timestamp
    modification_timestamp = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )