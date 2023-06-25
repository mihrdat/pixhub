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
    target_id = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())

    class Meta:
        model = Subscription
        fields = ["id", "subscriber_id", "target_id"]
        read_only_fields = ["subscriber_id"]

    def validate(self, attrs):
        subscriber_id = self.context["request"].user.author.pk
        target_id = attrs["target_id"]

        if subscriber_id == target_id:
            raise serializers.ValidationError(
                {"target_id": "You cannot subscribe to yourself."}
            )

        if Subscription.objects.filter(
            subscriber_id=subscriber_id, target_id=target_id
        ).exists():
            raise serializers.ValidationError(
                {"target_id": "You have already subscribed to this author."}
            )

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data["subscriber_id"] = self.context["request"].user.author.pk
        return super().create(validated_data)


class UnsubscribeSerializer(serializers.Serializer):
    target_id = serializers.IntegerField()


class RemoveSubscriptionSerializer(serializers.Serializer):
    subscriber_id = serializers.IntegerField()
