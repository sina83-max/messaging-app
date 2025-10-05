from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from starlette import status

from app.api.v1.users import user_dependency
from app.core.rate_limiter import rate_limiter
from app.crud.message import create_message, get_messages_for_user, generate_random_message, get_conversation, \
    mark_as_delivered, mark_as_read, get_filtered_messages
from app.crud.notification import create_notification
from app.db.session import db_dependency
from app.models.message import Message
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

    await rate_limiter(current_user.id, "send_message")

    # Create the message
    message = create_message(
        user=current_user,
        db=db,
        message=message
    )

    # Create notification
    create_notification(
        db=db,
        notification=Notification(
            user_id=message.recipient_id,
            type="message",
            content=f"New message from {current_user.username}"
        )
    )

    # Attempt to send email, but don't fail the request if it fails
    recipient = db.query(User).filter(User.id == message.recipient_id).first()
    if recipient and recipient.email:
        subject = "📩 New Message Received"
        body = f"""
            <h3>Hello {recipient.username},</h3>
            <p>You have received a new message:</p>
            <blockquote>{message.content}</blockquote>
            <p>Login to your account to reply.</p>
            """
        try:
            await send_email(subject, [recipient.email], body)
        except Exception as e:
            # Optionally log the error instead of raising
            print(f"Failed to send email: {e}")

    # Return the message regardless of email success
    return message



@router.get("/me", response_model=List[MessageResponse],
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


@router.get("/history", response_model=List[MessageResponse], status_code=status.HTTP_200_OK)
async def get_message_history(
    db: db_dependency,
    current_user: user_dependency       ,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Get all messages where the user is sender or receiver, paginated.
    """

    # Calculate pagination offsets
    skip = (page - 1) * page_size

    # Query messages (both sent and received)
    messages_query = (
        db.query(Message)
        .filter(
            (Message.sender_id == current_user.id)
            | (Message.recipient_id == current_user.id)
        )
        .order_by(Message.created_at.desc())
    )

    total_messages = messages_query.count()
    messages = messages_query.offset(skip).limit(page_size).all()

    return messages



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



