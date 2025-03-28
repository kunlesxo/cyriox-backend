import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = f"chat_{self.user.id}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = {"sender": self.user.username, "content": data["content"]}

        await self.channel_layer.group_send(
            f"chat_{data['receiver_id']}",
            {"type": "chat_message", "data": message},
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["data"]))
