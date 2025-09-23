from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.api.deps import get_current_user
from app.db.session import db_dependency
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateUsername

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

@router.patch("/me",
              response_model=UserResponse)
async def update_user(current_user: user_dependency,
                      db: db_dependency,
                      user_update: UserUpdateUsername = Depends()):
    existing_user = db.query(User).filter(User.username == user_update.username).first()
    print(existing_user)
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken"
        )
    else:
        current_user.username = user_update.username
        db.add(current_user)
        db.commit()
        db.refresh(current_user)

        return current_user