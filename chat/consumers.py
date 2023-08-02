import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class ChatPageConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = "test"
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        # Join room
        # self.channel_layer.group_add(self.room_group_name, self.channel_name)
        self.accept()

        self.send(
            text_data=json.dumps(
                {"type": "connection_established", "message": "You are now connected!"}
            )
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print(message)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "user_id": text_data_json["user_id"],
                "contact_id": text_data_json["contact_id"],
            },
        )

    def chat_message(self, event):
        message = event["message"]
        user_id = event["user_id"]
        contact_id = event["contact_id"]
        self.send(
            text_data=json.dumps(
                {
                    "type": "chat",
                    "message": message,
                    "user_id": user_id,
                    "contact_id": contact_id,
                }
            )
        )
