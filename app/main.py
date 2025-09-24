from fastapi import FastAPI
from app.api.v1 import auth, users, messages, notifications
from app.db.base import Base, engine

app = FastAPI(title="Messaging API")

Base.metadata.create_all(bind=engine)



app.include_router(auth.router,
                   prefix="/api/v1/auth",
                   tags=["auth"])
app.include_router(users.router,
                   prefix="/api/v1/users",
                   tags=["users"])
app.include_router(messages.router,
                   prefix="/api/v1/messages",
                   tags=["messages"])
app.include_router(notifications.router,
                   prefix="/api/v1/notifications",
                   tags=["notifications"])

