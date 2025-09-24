from fastapi import HTTPException
from sqlalchemy import and_

from app.db.session import db_dependency
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate


def create_notification(db: db_dependency,
                        notification: NotificationCreate):
    notification_new = Notification(
        user_id=notification.user_id,
        type = notification.type,
        content = notification.content
    )
    db.add(notification_new)
    db.commit()
    db.refresh(notification_new)

    return notification_new


def get_notification_for_user(db: db_dependency, user_id: int):
    notifications = db.query(Notification).filter(
        and_(
        Notification.user_id == user_id,
        Notification.is_read == False
        )
    ).all()
    return notifications or []


def mark_notification_read(db: db_dependency,
                           user_id: int,
                           notification_id: int):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    db.commit()
    db.refresh(notification)

    return notification


