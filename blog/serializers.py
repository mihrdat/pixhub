from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Author, Article, Subscription

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            "id",
            "bio",
            "subscribers_count",
            "subscriptions_count",
            "articles_count",
            "email",
        ]
        read_only_fields = [
            "subscribers_count",
            "subscriptions_count",
            "articles_count",
            "email",
        ]

    def get_email(self, author):
        return author.user.email


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["id", "title", "content", "created_at", "author"]
        read_only_fields = ["author"]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["author"] = request.user.author
        return super().create(validated_data)


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "subscriber", "target"]
        read_only_fields = ["subscriber"]

    def validate(self, attrs):
        subscriber = self.context["request"].user.author
        target = attrs["target"]

        if subscriber == target:
            raise serializers.ValidationError(
                {"target": "You cannot subscribe to yourself."}
            )
        if Subscription.objects.filter(subscriber=subscriber, target=target).exists():
            raise serializers.ValidationError(
                {"target": "You have already subscribed to this author."}
            )

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data["subscriber"] = self.context["request"].user.author
        return super().create(validated_data)


class UnsubscribeSerializer(serializers.Serializer):
    target = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())


class RemoveSubscriberSerializer(serializers.Serializer):
    subscriber = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
