from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from starlette import status

from app.api.v1.users import user_dependency
from app.crud.message import create_message, get_messages_for_user, generate_random_message, get_conversation, \
    mark_as_delivered, mark_as_read, get_filtered_messages
from app.crud.notification import create_notification
from app.db.session import db_dependency
from app.models.notification import Notification
from app.models.user import User
from app.schemas.message import MessageResponse, MessageCreate, MessageFilter
from app.services.email import send_email

router = APIRouter()


@router.get("/filter")
def filter_messages(
    db: db_dependency,
    current_user: user_dependency,
    keyword: Optional[str] = Query(None, description="Search in message content"),
    sender_id: Optional[int] = Query(None, description="Filter by sender"),
    unread_only: Optional[bool] = Query(False, description="Only unread messages"),
    date_from: Optional[datetime] = Query(None, description="Filter from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter until this date"),
):

    return get_filtered_messages(
        db=db,
        user_id=current_user.id,
        keyword=keyword,
        sender_id=sender_id,
        unread_only=unread_only,
        date_from=date_from,
        date_to=date_to,
    )



@router.post("/", response_model=MessageResponse,
             status_code=status.HTTP_201_CREATED)
async def create_message_endpoint(message: MessageCreate,
                         db: db_dependency,
                         current_user: user_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    message = create_message(
        user=current_user,
        db=db,
        message=message
    )

    create_notification(
        db=db,
        notification=Notification(
            user_id = message.recipient_id,
            type="message",
            content=f"New message from {current_user.username}"
        )
    )
    recipient = db.query(User).filter(User.id == message.recipient_id).first()
    if recipient and recipient.email:
        subject = "📩 New Message Received"
        body = f"""
            <h3>Hello {recipient.username},</h3>
            <p>You have received a new message:</p>
            <blockquote>{message.content}</blockquote>
            <p>Login to your account to reply.</p>
            """
        await send_email(subject, [recipient.email], body)

    return message


@router.get("/me", response_model=MessageResponse,
            status_code=status.HTTP_200_OK)
async def get_messages(db: db_dependency, current_user: user_dependency):
    messages = get_messages_for_user(
        db=db,
        user_id=current_user.id
    )
    return messages

@router.get("/random", status_code=status.HTTP_200_OK)
async def get_random_message(db: db_dependency, current_user: user_dependency):
    return generate_random_message()


@router.get("/{user_id}", response_model=List[MessageResponse],
            status_code=status.HTTP_200_OK)
async def get_conversation_endpoint(db: db_dependency,
                           current_user: user_dependency,
                           user_id: int):
    conversation = get_conversation(
        db=db,
        user1_id=current_user.id,
        user2_id=user_id
    )
    return conversation

@router.patch("/{message_id}/mark_as_delivered",
              response_model=MessageResponse,
              status_code=status.HTTP_200_OK)
async def mark_message_delivered_endpoint(db: db_dependency,
                                          user: user_dependency,
                                          message_id: int):
    message = mark_as_delivered(
        db=db,
        user_id=user.id,
        message_id=message_id
    )

    return message

@router.patch("/{message_id}/mark_as_read",
              response_model=MessageResponse,
              status_code=status.HTTP_200_OK)
async def mark_message_read_endpoint(db: db_dependency,
                                          user: user_dependency,
                                          message_id: int):
    message = mark_as_read(
        db=db,
        user_id=user.id,
        message_id=message_id
    )

    return message




