from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MessageCreate(BaseModel):
    recipient_id: int
    content: str


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    content: str
    is_delivered: bool
    is_read: bool
    created_at: datetime

    class Config:
        from_attribute = True


class MessageResponseWithUsername(BaseModel):
    id: int
    sender_id: int
    sender_username: str
    recipient_id: int
    recipient_username: str
    content: str
    is_delivered: bool
    is_read: bool
    created_at: datetime

    class Config:
        from_attribute = True



class MessageFilter(BaseModel):
    keyword: Optional[str] = None
    sender_id: Optional[int] = None
    unread_only: Optional[bool] = False
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None