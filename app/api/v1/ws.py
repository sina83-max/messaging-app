import asyncio
import json

from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.v1.users import user_dependency
from app.core.connection_manager import ConnectionManager, manager

router = APIRouter()


@router.websocket("/chat/")
async def chat(current_user: user_dependency,
               web_socket: WebSocket):

    user_id = current_user.id
    await manager.connect(user_id, web_socket)

    asyncio.create_task(manager.subscribe_to_redis(f"user: {user_id}"))

    try:
        while True:
            data = await web_socket.receive_text()
            message_data = json.loads(data)

            if "recipient_id" not in message_data or "content" not in message_data:
                await web_socket.send_text(json.dumps({"error": "Invalid message format"}))
                continue

            # message_data should include:
            # {"recipient_id": 2, "content": "Hello!"}

            await manager.send_personal_message(message_data.get("recipient_id"), message_data)
            await manager.publish_to_redis(f"user {user_id}", message_data)

    except WebSocketDisconnect:
        manager.disconnect(user_id)

