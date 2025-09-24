from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: int
    type: str
    content: str


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True
        

class NotificationFilter(BaseModel):
    user_id: Optional[int] = None
    type: Optional[str] = None
    unread_only: Optional[bool] = False
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None