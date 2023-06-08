from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Author, Relation, Article

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


class RelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relation
        fields = ["id", "subscriber", "target"]
        read_only_fields = ["subscriber"]

    def validate(self, attrs):
        subscriber = self.context["request"].user.author
        target = attrs["target"]

        if subscriber == target:
            raise serializers.ValidationError(
                {"target": "You cannot subscribe to yourself."}
            )

        if Relation.objects.filter(subscriber=subscriber, target=target).exists():
            raise serializers.ValidationError(
                {"target": "You have already subscribed to this author."}
            )

        return super().validate(attrs)


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["id", "title", "content", "created_at", "author"]
        read_only_fields = ["author"]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["author"] = request.user.author
        return super().create(validated_data)
