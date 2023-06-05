from django.db import transaction
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
        fields = ["id", "bio", "subscribers_count", "subscriptions_count", "user"]
        read_only_fields = ["subscribers_count", "subscriptions_count"]


class SimpleAuthorSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Author
        fields = ["id", "bio", "user"]


class SubscriptionSerializer(serializers.ModelSerializer):
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

    @transaction.atomic()
    def create(self, validated_data):
        validated_data["subscriber"] = self.context["request"].user.author
        instance = super().create(validated_data)

        subscriber = instance.subscriber
        subscriber.subscriptions_count += 1
        subscriber.save(update_fields=["subscriptions_count"])

        target = instance.target
        target.subscribers_count += 1
        target.save(update_fields=["subscribers_count"])

        return instance


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["id", "title", "content", "created_at", "author"]
        read_only_fields = ["author"]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["author"] = request.user.author
        return super().create(validated_data)
