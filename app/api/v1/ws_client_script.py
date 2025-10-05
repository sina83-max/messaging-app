import websocket
import json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmcxMCIsInVzZXJfaWQiOjE1LCJleHAiOjE3NjIyMzczMzV9.vkx47-DXG6tOtVI7dBi0uTWwV95gbFXjJnwsb9uAR6o"
url = f"ws://localhost:8000/api/v1/ws/chat?token={token}"

ws = websocket.WebSocket()
ws.connect(url)

# Send a message
ws.send(json.dumps({"recipient_id": 2, "content": "Hello"}))

# Receive a message
response = ws.recv()
print(response)

ws.close()
