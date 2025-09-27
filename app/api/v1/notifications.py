from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr

from app.api.v1.users import user_dependency
from app.crud.notification import get_notification_for_user, mark_notification_read
from app.db.session import db_dependency
from app.schemas.notification import NotificationResponse
from app.services.email import send_email

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(db: db_dependency,
                            user: user_dependency):

    notifications = get_notification_for_user(db, user.id)

    return notifications

@router.patch("/{notification_id}/read",
              response_model=NotificationResponse,
              status_code=status.HTTP_200_OK)
async def mark_notification_read_endpoint(
        db: db_dependency,
        notification_id: int,
        current_user: user_dependency):
    notification = mark_notification_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return notification

@router.post("/send-email")
async def send_test_email(recipient: EmailStr):
    await send_email(
        subject="Test Notification",
        recipients=[recipient],
        body="<h3>Hello from Messaging App</h3><p>This is a test email.</p>"
    )
    return {"message": f"Email sent to {recipient}"}
