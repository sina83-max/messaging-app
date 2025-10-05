from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from typing import Annotated, List

from starlette import status

from app.api.deps import get_current_admin
from app.core.presence_manager import get_online_users
from app.db.session import db_dependency
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter()

admin_dependency = Annotated[dict, Depends(get_current_admin)]


@router.get("/users")
def list_all_users(
        db: db_dependency,
        admin: admin_dependency
):
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this resource",
        )
    return db.query(User).all()

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
        user_id: int,
        db: db_dependency,
        admin: admin_dependency
):
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this resource",
        )
    return db.query(User).filter(User.id == user_id).first()

@router.get('/actives',
            response_model=List[str],
            status_code=status.HTTP_200_OK)
async def list_actives(db: db_dependency):

    online_user_ids = await get_online_users()
    online_user_ids = [int(uid) for uid in online_user_ids]

    users = db.query(User).filter(User.id.in_(online_user_ids)).all()

    usernames = [user.username for user in users]

    return usernames