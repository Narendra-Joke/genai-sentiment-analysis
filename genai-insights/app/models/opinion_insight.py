from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Enum,
    Float,
    DateTime,
    DECIMAL,
    func,
    Date,
    ForeignKey
)
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

from app.db.base import Base

class OpinionInsight(Base):
    __tablename__ = "opinion_insights"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Timestamps
    creation_date = Column(
        DateTime,
        server_default=func.current_timestamp()
    )

    review_date = Column(
        Date,
        nullable=True
    )

    modification_timestamp = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # Core Review Fields (MANDATORY LOGICALLY)
    product_name = Column(String(40), nullable=True)
    source = Column(String(25), nullable=True)
    content = Column(Text, nullable=False)

    # Optional Metadata
    author = Column(String(255), nullable=True)
    country = Column(String(35), nullable=True)
    extra = Column(String(250), nullable=True)

    # Sentiment Fields
    sentiment = Column(
        Enum("positive", "negative", "neutral", name="sentiment"),
        nullable=True
    )

    sentiment_confidence = Column(
        DECIMAL(5, 4),
        nullable=True
    )

    rating = Column(Float, nullable=True)

    # Processing State Flags (CRITICAL)
    sentiment_classified = Column(Integer, nullable=False, default=0)
    component_classified = Column(Integer, nullable=False, default=0)

    # Component Context
    component = Column(String(25), nullable=True, default="overallphone")

    job_id = Column(
    Integer,
    ForeignKey(
        "job_status.id",
        ondelete="SET NULL",
        onupdate="CASCADE"
    ),
    nullable=True,
    index=True
    )
