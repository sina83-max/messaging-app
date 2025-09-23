from typing import Annotated

from fastapi import Depends

from app.db.base import Session


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]