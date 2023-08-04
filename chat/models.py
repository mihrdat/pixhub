from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Room(models.Model):
    name = models.CharField(max_length=55)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms")
    contact = models.ForeignKey(User, on_delete=models.CASCADE)


class ChatPage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_pages")
    contact = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.contact.email


class Message(models.Model):
    content = models.TextField()
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.email} to {self.recipient.email}: {self.content}"
