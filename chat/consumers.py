import json

from urllib.parse import parse_qsl
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = await self.get_room_name()

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        user = self.scope["user"]
        query_params = dict(parse_qsl(self.scope["query_string"].decode("utf-8")))
        contact_id = query_params["contact_id"]

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
            },
        )

        # Save message in the database
        await self.save_message(message, user.id, contact_id)

    @database_sync_to_async
    def save_message(self, content, sender_id, recipient_id):
        return Message.objects.create(
            content=content, sender_id=sender_id, recipient_id=recipient_id
        )

    async def chat_message(self, event):
        message = event["message"]

        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat",
                    "message": message,
                }
            )
        )

    async def get_room_name(self):
        user = self.scope["user"]
        query_params = dict(parse_qsl(self.scope["query_string"].decode("utf-8")))
        contact_id = query_params["contact_id"]
        return "-".join(sorted([str(user.id), str(contact_id)]))
