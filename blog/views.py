from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
)
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Author, Subscription, Article, LikedItem
from .serializers import (
    AuthorSerializer,
    SubscriptionCreateSerializer,
    ArticleSerializer,
    UnsubscribeSerializer,
    RemoveSubscriberSerializer,
    SimpleAuthorSerializer,
    LikeSerializer,
)
from .permissions import IsOwnerOrReadOnly, HasAccessAuthorContent
from .pagination import DefaultLimitOffsetPagination
from .throttling import SubscriptionUserRateThrottle


class AuthorViewSet(
    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    queryset = Author.objects.select_related("user")
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = DefaultLimitOffsetPagination
    filter_backends = [SearchFilter]
    search_fields = ["user__email"]

    @action(methods=["GET", "PUT", "PATCH"], detail=False)
    def me(self, request, *args, **kwargs):
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        if request.method == "PUT":
            return self.update(request, *args, **kwargs)
        if request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)

    @action(methods=["GET"], detail=True)
    def subscriptions(self, request, *args, **kwargs):
        author = self.get_object()
        self.queryset = Subscription.objects.get_subscriptions_for(author)
        return self.list(request, *args, **kwargs)

    @action(methods=["GET"], detail=True)
    def subscribers(self, request, *args, **kwargs):
        author = self.get_object()
        self.queryset = Subscription.objects.get_subscribers_for(author)
        return self.list(request, *args, **kwargs)

    @action(methods=["GET"], detail=True)
    def articles(self, request, *args, **kwargs):
        author = self.get_object()
        self.queryset = Article.objects.filter(author=author).order_by("-created_at")
        return self.list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ["subscriptions", "subscribers"]:
            self.serializer_class = SimpleAuthorSerializer
        if self.action == "articles":
            self.serializer_class = ArticleSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ["subscriptions", "subscribers", "articles"]:
            self.permission_classes = [IsAuthenticated, HasAccessAuthorContent]
        return super().get_permissions()

    def get_object(self):
        if self.action == "me":
            return self.get_current_author()
        return super().get_object()

    def get_current_author(self):
        return self.request.user.author


class SubscriptionViewSet(CreateModelMixin, GenericViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionCreateSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [SubscriptionUserRateThrottle]

    @action(methods=["DELETE"], detail=False)
    def unsubscribe(self, request, *args, **kwargs):
        return self.destroy_subscription(request, *args, **kwargs)

    @action(methods=["DELETE"], detail=False)
    def remove(self, request, *args, **kwargs):
        return self.destroy_subscription(request, *args, **kwargs)

    def destroy_subscription(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object(serializer.validated_data)
        self.perform_destroy_subscription(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @transaction.atomic
    def perform_destroy_subscription(self, instance):
        subscriber = instance.subscriber
        target = instance.target

        subscriber.subscriptions_count -= 1
        subscriber.save(update_fields=["subscriptions_count"])
        target.subscribers_count -= 1
        target.save(update_fields=["subscribers_count"])

        instance.delete()

    @transaction.atomic
    def perform_create(self, serializer):
        subscriber = self.get_current_author()
        target = serializer.validated_data["target"]

        subscriber.subscriptions_count += 1
        subscriber.save(update_fields=["subscriptions_count"])
        target.subscribers_count += 1
        target.save(update_fields=["subscribers_count"])

        return super().perform_create(serializer)

    def get_serializer_class(self):
        if self.action == "unsubscribe":
            self.serializer_class = UnsubscribeSerializer
        if self.action == "remove":
            self.serializer_class = RemoveSubscriberSerializer
        return super().get_serializer_class()

    def get_object(self, validated_data):
        current_author = self.get_current_author()
        if self.action == "unsubscribe":
            return Subscription.objects.get(
                subscriber=current_author, target=validated_data["target"]
            )
        if self.action == "remove":
            return Subscription.objects.get(
                subscriber=validated_data["subscriber"], target=current_author
            )
        return super().get_object()

    def get_current_author(self):
        return self.request.user.author


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = DefaultLimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["author"]

    @transaction.atomic
    def perform_create(self, serializer):
        current_author = self.get_current_author()
        current_author.articles_count += 1
        current_author.save(update_fields=["articles_count"])
        return super().perform_create(serializer)

    @transaction.atomic
    def perform_destroy(self, instance):
        author = instance.author
        author.articles_count -= 1
        author.save(update_fields=["articles_count"])
        return super().perform_destroy(instance)

    def get_queryset(self):
        current_author = self.get_current_author()
        subscriptions = Subscription.objects.get_subscriptions_for(current_author)

        return (
            super()
            .get_queryset()
            .filter(Q(author__in=subscriptions) | Q(author=current_author))
            .order_by("-created_at")
        )

    def get_current_author(self):
        return self.request.user.author


class LikeViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    queryset = LikedItem.objects.select_related("author__user")
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination

    @action(methods=["DELETE"], detail=False)
    def dislike(self, request, *args, **kwargs):
        return self.destroy_like(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        article = Article.objects.get(pk=self.kwargs["article_pk"])
        article.likes_count += 1
        article.save(update_fields=["likes_count"])
        return super().perform_create(serializer)

    def destroy_like(self, request, *args, **kwargs):
        instance = get_object_or_404(
            LikedItem,
            author=self.get_current_author(),
            article_id=self.kwargs["article_pk"],
        )
        self.perform_destroy_like(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @transaction.atomic
    def perform_destroy_like(self, instance):
        article = instance.article

        article.likes_count -= 1
        article.save(update_fields=["likes_count"])

        instance.delete()

    def get_queryset(self):
        article_id = self.kwargs["article_pk"]
        return LikedItem.objects.get_likes_for(article_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["article_id"] = self.kwargs["article_pk"]
        return context

    def get_current_author(self):
        return self.request.user.author

    def get_serializer_class(self):
        if self.action == "list":
            self.serializer_class = SimpleAuthorSerializer
        return super().get_serializer_class()
