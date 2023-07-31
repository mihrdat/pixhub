import json
from channels.generic.websocket import WebsocketConsumer


class ChatPageConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["chat_page"]
        # self.room_group_name = "chat_%s" % self.room_name

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
