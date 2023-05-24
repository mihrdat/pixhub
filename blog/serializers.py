from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Author, Subscription

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]


class AuthorSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Author
        fields = ["id", "bio", "user"]


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
                {"error": "You cannot subscribe to yourself."}
            )

        if Subscription.objects.filter(subscriber=subscriber, author=author).exists():
            raise serializers.ValidationError(
                {"error": "You have already subscribed to this author."}
            )

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data["subscriber"] = self.context["request"].user.author
        return super().create(validated_data)
