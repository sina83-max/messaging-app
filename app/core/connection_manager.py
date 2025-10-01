import json
from typing import Dict

from starlette.websockets import WebSocket

from app.core.redis import redis


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[int, WebSocket] = {}
        print("Create a list holding active connections", self.active_connections)

    async def connect(self, user_id: int, web_socket: WebSocket):
        await web_socket.accept()
        if not self.active_connections.get(user_id):
            self.active_connections[user_id] = []
        self.active_connections[user_id] = web_socket
        print("New active connections are: ", self.active_connections)

    async def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)
        print("Active connections after disconnecting are: ", self.active_connections)

    async def send_personal_message(self,
                                    user_id: int,
                                    message: dict):
        web_socket = self.active_connections.get(user_id)
        if web_socket:
            try:
                await web_socket.send_text(json.dumps(message))
                print("A personal message has been sent to: ", web_socket)
            except:
                self.disconnect(user_id)

    async def publish_to_redis(self, channel: str, message: dict):
        await redis.publish(channel, json.dumps(message))

    async def subscribe_to_redis(self, channel: str):
        pubsub = redis.pubsub()
        await pubsub.subscribe(channel)

        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await self.send_personal_message(data['recipient_id'], data)


manager = ConnectionManager()