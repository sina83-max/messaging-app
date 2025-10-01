from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(50), nullable=True, unique=True)
    hashed_password = Column(String(100), nullable=False)
    avatar_url = Column(String(100), nullable=True)
    role = Column(String(50), nullable=False, default="user")
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True)