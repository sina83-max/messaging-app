from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.jwt import decode_access_token
from app.db.session import db_dependency
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')

def get_current_user(db: db_dependency,
                     token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        user_id = payload.get('user_id')
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail='Could not validate credentials',
                headers={'WWW-Authenticate': 'Bearer'}
            )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail='User not found',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return user
