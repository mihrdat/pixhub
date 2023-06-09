from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Author, Article

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


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["id", "title", "content", "created_at", "author"]
        read_only_fields = ["author"]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["author"] = request.user.author
        return super().create(validated_data)
