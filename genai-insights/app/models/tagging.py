from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime
)
from sqlalchemy.sql import func

from app.db.base import Base


class Tagging(Base):
    __tablename__ = "tagging1"

    id = Column(Integer, primary_key=True, autoincrement=True)

    component = Column(String(50), nullable=False)

    tag = Column(String(100), nullable=False)

    terms = Column(Text, nullable=False)

    creation_timestamp = Column(
        DateTime,
        server_default=func.current_timestamp()
    )

    modification_timestamp = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
