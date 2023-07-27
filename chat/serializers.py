from rest_framework import serializers
from .models import ChatPage


class ChatPageSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = ChatPage
        fields = ["id", "name"]

    def get_name(self, chat_page):
        return chat_page.contact.email
