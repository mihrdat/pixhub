from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=255, blank=True, null=True)


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="subscriptions"
    )
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="subscribers"
    )

    class Meta:
        unique_together = ["subscriber", "author"]

    def __str__(self):
        return f"{self.subscriber} subscribed to {self.author}"


class Article(models.Model):
    slug = models.SlugField(primary_key=True, max_length=255)
    title = models.CharField(max_length=255)
    content = models.TextField(max_length=255, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="blogs")
