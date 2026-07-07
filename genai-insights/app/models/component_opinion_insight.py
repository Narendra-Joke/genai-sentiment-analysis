from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Enum,
    DateTime,
    ForeignKey,
    Date
)
from sqlalchemy.sql import func

from app.db.base import Base

class ComponentOpinionInsight(Base):
    __tablename__ = "component_opinion_insights"

    id = Column(Integer, primary_key=True, autoincrement=True)

    parent_id = Column(
        Integer,
        ForeignKey(
            "opinion_insights.id",
            ondelete="SET NULL",
            onupdate="CASCADE"
        ),
        nullable=True
    )

    creation_date = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False
    )

    review_date = Column(
        Date,
        nullable=True
    )

    product_name = Column(String(40), nullable=True)

    source = Column(String(25), nullable=True)

    author = Column(String(100), nullable=True)

    country = Column(String(35), nullable=True)

    content = Column(
        Text,
        nullable=True
    )

    component = Column(String(25), nullable=False)

    sentiment = Column(
        Enum("positive", "negative", "neutral"),
        nullable=True
    )

    rating = Column(Float, nullable=True)

    sentiment_confidence = Column(Float, nullable=True)

    extra = Column(String(250), nullable=True)

    modification_timestamp = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )

    sentiment_classified = Column(
        Integer,
        nullable=False,
        default=0
    )

    tags = Column(String(500), nullable=True)

    tagging_classified = Column(
        Integer,
        nullable=False,
        default=0
    )

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
