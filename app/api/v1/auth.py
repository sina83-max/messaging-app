from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from starlette import status

from app.core.config import settings
from app.core.jwt import create_access_token
from app.core.minio_client import upload_avatar
from app.schemas.user import UserCreate, UserLogin
from app.core.security import Hasher
from app.db.session import db_dependency
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED,
             response_model=UserResponse)
async def create_user(db: db_dependency,
                      username: str = Form(...),
                      email: EmailStr = Form(...),
                      password: str = Form(...),
                      avatar: UploadFile | None = File(None)):
    existing_user = db.query(User).filter(
        User.username == username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {username} already exists"
        )

    hashed_password = Hasher.hash_password(password)

    user_model = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
    )

    if avatar:
        try:
            avatar_url = upload_avatar(avatar, user_id=0)
            user_model.avatar_url = avatar_url
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Avatar upload failed: {str(e)}"
            )
    db.add(user_model)
    db.commit()
    db.refresh(user_model)

    if avatar:
        user_model.avatar_url = upload_avatar(avatar,
                                              user_id=user_model.id)
        db.add(user_model)
        db.commit()
        db.refresh(user_model)

    return {"msg": "User registered", "id": user_model.id, "avatar": user_model.avatar}

@router.post("/login", status_code=status.HTTP_200_OK, response_model=None)
async def login_user(db: db_dependency,
                     user_login: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.username == user_login.username).first()
    if not user or not Hasher.verify_password(
            user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token_expires = timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            'sub': user.username,
            'user_id': user.id
        },
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
