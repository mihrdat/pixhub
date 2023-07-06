from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Author, Article, Subscription, LikedItem

User = get_user_model()


class SimpleAuthorSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ["id", "email"]

    def get_email(self, author):
        return author.user.email


class AuthorSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            "id",
            "bio",
            "email",
            "subscribers_count",
            "subscriptions_count",
            "articles_count",
        ]
        read_only_fields = [
            "email",
            "subscribers_count",
            "subscriptions_count",
            "articles_count",
        ]

    def get_email(self, author):
        return author.user.email


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["id", "title", "content", "created_at", "author", "likes_count"]
        read_only_fields = ["author", "likes_count"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user.author
        return super().create(validated_data)


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "subscriber", "target"]
        read_only_fields = ["subscriber"]

    def validate(self, data):
        subscriber = self.context["request"].user.author
        target = data["target"]

        if subscriber == target:
            raise serializers.ValidationError(
                {"target": "You cannot subscribe to yourself."}
            )

        if Subscription.objects.filter(subscriber=subscriber, target=target).exists():
            raise serializers.ValidationError(
                {"target": "You have already subscribed to this author."}
            )

        return super().validate(data)

    def create(self, validated_data):
        validated_data["subscriber"] = self.context["request"].user.author
        return super().create(validated_data)


class UnsubscribeSerializer(serializers.Serializer):
    target = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())

    def validate(self, data):
        current_author = self.context["request"].user.author
        target = data["target"]

        if not Subscription.objects.filter(
            subscriber=current_author, target=target
        ).exists():
            raise serializers.ValidationError(
                {"target": "No existing subscription for the specified author."}
            )

        return super().validate(data)


class RemoveSubscriberSerializer(serializers.Serializer):
    subscriber = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())

    def validate(self, data):
        current_author = self.context["request"].user.author
        subscriber = data["subscriber"]

        if not Subscription.objects.filter(
            subscriber=subscriber, target=current_author
        ).exists():
            raise serializers.ValidationError(
                {"subscriber": "The author you provided is not subscribed to you."}
            )

        return super().validate(data)


class LikeSerializer(serializers.ModelSerializer):
    author = SimpleAuthorSerializer(read_only=True)

    class Meta:
        model = LikedItem
        fields = ["author"]

    def validate(self, data):
        current_author = self.context["request"].user.author
        article_id = self.context["article_id"]

        if LikedItem.objects.filter(
            author=current_author, article_id=article_id
        ).exists():
            raise serializers.ValidationError(
                {"author": "You have already liked this article."}
            )

        return super().validate(data)

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user.author
        validated_data["article_id"] = self.context["article_id"]
        return super().create(validated_data)
