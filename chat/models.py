from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Message(models.Model):
    content = models.TextField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.user.email} to {self.recipient.email}: {self.content}"
