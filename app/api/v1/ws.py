import asyncio
import json

from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.v1.users import user_dependency
from app.core.connection_manager import ConnectionManager, manager
from app.core.jwt import decode_access_token
from app.core.presence_manager import set_user_online, set_user_offline
from app.db.session import db_dependency
from app.models.user import User

router = APIRouter()


async def get_current_user_ws(websocket: WebSocket, db):
    token = websocket.query_params.get("token")
    print("Token received:", token)
    if not token:
        await websocket.close(code=1008)
        return None

    try:
        payload = decode_access_token(token)
        print("Decoded payload:", payload)
        user_id = payload.get("user_id")
        if not user_id:
            await websocket.close(code=1008)
            return None
        user = db.query(User).filter(User.id == user_id).first()
        print("User found:", user)
        if not user:
            await websocket.close(code=1008)
            return None
        return user
    except Exception as e:
        print("Exception decoding JWT:", e)
        await websocket.close(code=1008)
        return None


@router.websocket("/chat/")
async def chat(web_socket: WebSocket):
    db = db_dependency()
    # DON'T accept here - authenticate first
    user = await get_current_user_ws(web_socket, db)

    if not user:
        return

    user_id = user.id

    # Accept the connection NOW, after authentication
    await web_socket.accept()
    await manager.connect(user_id, web_socket)
    await set_user_online(user_id)
    await manager.broadcast({"event": "user_status", "user_id": user_id, "status": "online"})


    asyncio.create_task(manager.subscribe_to_redis(f"user {user_id}"))

    try:
        while True:
            data = await web_socket.receive_text()
            message_data = json.loads(data)

            if "recipient_id" not in message_data or "content" not in message_data:
                await web_socket.send_text(json.dumps({"error": "Invalid message format"}))
                continue

            await manager.send_personal_message(message_data.get("recipient_id"), message_data)
            await manager.publish_to_redis(f"user {user_id}", message_data)

    except WebSocketDisconnect:
        await manager.disconnect(user_id)
        await set_user_offline(user_id)
        await manager.broadcast({"event": "user_status", "user_id": user_id, "status": "offline"})