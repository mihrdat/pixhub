from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Author(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=255, blank=True, null=True)
    subscribers_count = models.PositiveIntegerField(default=0)
    subscriptions_count = models.PositiveIntegerField(default=0)
    articles_count = models.PositiveIntegerField(default=0)
    is_private = models.BooleanField(default=False)


class SubscriptionManager(models.Manager):
    def get_subscriptions_for(self, author_id):
        return (
            Author.objects.filter(subscribers__subscriber_id=author_id)
            .select_related("user")
            .order_by("-created_at")
        )

    def get_subscribers_for(self, author_id):
        return (
            Author.objects.filter(subscriptions__target_id=author_id)
            .select_related("user")
            .order_by("-created_at")
        )


class Subscription(BaseModel):
    objects = SubscriptionManager()
    subscriber = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="subscriptions"
    )
    target = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="subscribers"
    )

    class Meta:
        unique_together = ["subscriber", "target"]


class ArticleManager(models.Manager):
    def get_articles_for(self, author_id):
        return Article.objects.filter(author_id=author_id).order_by("-created_at")


class Article(BaseModel):
    objects = ArticleManager()
    title = models.CharField(max_length=55)
    content = models.TextField(max_length=255, blank=True, null=True)
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="articles"
    )

    @property
    def user(self):
        return self.author.user
