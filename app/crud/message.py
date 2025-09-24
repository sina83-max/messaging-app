import random

from fastapi import HTTPException
from sqlalchemy import or_, and_
from starlette import status

from app.api.v1.users import user_dependency
from app.db.session import db_dependency
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageFilter

random_messages = [
    "Hello! How are you?",
    "Don't forget to check your tasks!",
    "Have a great day!",
    "Random fact: FastAPI is awesome!"
]


def create_message(db: db_dependency,
                   user: user_dependency,
                   message: MessageCreate):
    new_message = Message(
        sender_id=user.id,
        recipient_id=message.recipient_id,
        content=message.content,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message


def get_messages_for_user(db: db_dependency, user_id: int):
    messages = db.query(Message).filter(Message.recipient_id == user_id).all()

    return messages


def get_conversation(db: db_dependency, user1_id: int, user2_id: int):
    messages = db.query(Message).filter(
        or_(
            (Message.sender_id == user1_id) & (Message.recipient_id == user2_id),
            (Message.sender_id == user2_id) & (Message.recipient_id == user1_id)
        )
    ).order_by(Message.created_at.asc()).all()

    return messages or []


def generate_random_message():
    return random.choice(random_messages)


def mark_as_delivered(db: db_dependency,
                      message_id: int,
                      user_id: int):
    message = db.query(Message).filter(
        and_(
            Message.recipient_id == user_id,
            Message.id == message_id
        )
    ).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    message.is_delivered = True
    db.commit()
    db.refresh(message)

    return message


def mark_as_read(db: db_dependency,
                 message_id: int,
                 user_id: int):
    message = db.query(Message).filter(
        and_(
            Message.recipient_id == user_id,
            Message.id == message_id
        )
    ).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    message.is_read = True
    db.commit()
    db.refresh(message)

    return message

