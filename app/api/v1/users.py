from datetime import timezone, datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from starlette import status

from app.api.deps import get_current_user
from app.core.minio_client import upload_avatar
from app.core.security import Hasher
from app.db.session import db_dependency
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateProfile, UserUpdatePassword

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/me",
            response_model=UserResponse,
            status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user



@router.patch("/me", response_model=UserResponse)
async def update_profile(
    current_user: user_dependency,
    db: db_dependency,
    username: str | None = Form(None),
    avatar: UploadFile | None = File(None)
):
    updated = False  # Track if any field changed

    # Update username if provided
    if username and username != current_user.username:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already taken"
            )
        current_user.username = username
        updated = True

    # Update avatar if provided
    if avatar:
        try:
            avatar_url = upload_avatar(avatar, user_id=current_user.id)
            current_user.avatar_url = avatar_url
            updated = True
        except Exception as e:
            # Log error but don’t block other updates
            print(f"Avatar upload failed: {str(e)}")

    # Update timestamp only if something changed
    if updated:
        current_user.updated_at = datetime.now(timezone.utc)
        db.add(current_user)
        db.commit()
        db.refresh(current_user)

    return current_user



@router.patch("/reset-password",
             response_model=UserResponse)
async def reset_password(current_user: user_dependency,
                         db: db_dependency,
    ):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not Hasher.verify_password(user_update.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not match"
        )
    if not user_update.new_password == user_update.repeat_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords does not match"
        )
    user.hashed_password = Hasher.hash_password(user_update.new_password)
    user.updated_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)

    return user