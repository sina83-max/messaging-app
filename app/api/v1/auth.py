from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.core.config import settings
from app.core.jwt import create_access_token
from app.schemas.user import UserCreate, UserLogin
from app.core.security import Hasher
from app.db.session import db_dependency
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED,
             response_model=UserResponse)
async def create_user(create_user_request: UserCreate, db: db_dependency):
    existing_user = db.query(User).filter(
        User.username == create_user_request.username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {create_user_request .get('username')} already exists"
        )

    hashed_password = Hasher.hash_password(create_user_request.password)

    user_model = User(
        username=create_user_request.username,
        email=create_user_request.email,
        hashed_password=hashed_password,
    )
    db.add(user_model)
    db.commit()

    return user_model

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
