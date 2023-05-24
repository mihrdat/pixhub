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

    def create(self, validated_data):
        validated_data["subscriber"] = self.context["request"].user.author
        return super().create(validated_data)
