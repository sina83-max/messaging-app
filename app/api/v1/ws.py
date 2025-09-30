from fastapi import APIRouter
from starlette.websockets import WebSocket

from app.api.v1.users import user_dependency
from app.core.connection_manager import ConnectionManager

router = APIRouter()


@router.websocket("/chat/{user_id}")
async def chat(current_user: user_dependency,
               web_socket: WebSocket,
               user_id: int):
    await web_socket.accept()
    manager = ConnectionManager()
    manager.connect(current_user.id, web_socket)
    manager.subscribe_to_redis()