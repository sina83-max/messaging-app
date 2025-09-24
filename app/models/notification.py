from datetime import datetime, timezone

from sqlalchemy import Column, Integer, ForeignKey, Enum as SAEnum, String, Boolean, DateTime
from enum import Enum
from app.db.base import Base


class TypeEnum(str, Enum):
    message = "message"
    system = "system"


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(SAEnum(TypeEnum), nullable=False)
    content = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))