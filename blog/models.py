from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=255, blank=True, null=True)
    subscribers_count = models.PositiveIntegerField(default=0)
    subscriptions_count = models.PositiveIntegerField(default=0)
    articles_count = models.PositiveIntegerField(default=0)
    is_private = models.BooleanField(default=False)


class SubscriptionManager(models.Manager):
    def get_subscriptions_for(self, author):
        return Author.objects.filter(subscribers__subscriber=author)

    def get_subscribers_for(self, author):
        return Author.objects.filter(subscriptions__target=author)


class Subscription(models.Model):
    objects = SubscriptionManager()
    subscriber = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="subscriptions"
    )
    target = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="subscribers"
    )

    class Meta:
        unique_together = ["subscriber", "target"]


class Article(models.Model):
    title = models.CharField(max_length=55)
    content = models.TextField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="articles"
    )
