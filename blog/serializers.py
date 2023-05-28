from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Author, Subscription, Article

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]


class AuthorSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Author
        fields = ["id", "bio", "user", "subscribers_count", "subscriptions_count"]


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Subscription
        fields = ["id", "subscriber", "author"]

    def validate(self, attrs):
        subscriber = self.context["request"].user.author
        author = attrs["author"]

        if subscriber == author:
            raise serializers.ValidationError(
                {"author": "You cannot subscribe to yourself."}
            )

        if Subscription.objects.filter(subscriber=subscriber, author=author).exists():
            raise serializers.ValidationError(
                {"author": "You have already subscribed to this author."}
            )

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data["subscriber"] = self.context["request"].user.author
        return super().create(validated_data)


class ArticleSerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "slug",
            "created_at",
            "author",
        ]

    def get_slug(self, article):
        return slugify(f"{article.title}-{article.created_at}")


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["title", "content"]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["author"] = request.user.author
        return super().create(validated_data)
