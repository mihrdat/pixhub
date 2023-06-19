from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Author, Subscription
from .serializers import (
    AuthorSerializer,
    SubscriptionSerializer,
    SubscriptionCreateSerializer,
)
from .permissions import IsOwnerOrReadOnly
from .pagination import DefaultLimitOffsetPagination


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
        self.get_object = self.get_current_author
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)

    def get_current_author(self):
        return super().get_queryset().get(user=self.request.user)


class SubscriptionViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Subscription.objects.select_related("subscriber__user", "target__user")
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["subscriber", "target"]

    def get_queryset(self):
        current_author = self.request.user.author
        return (
            super()
            .get_queryset()
            .filter(Q(subscriber=current_author) | Q(target=current_author))
        )

    def get_serializer_class(self):
        if self.action == "create":
            self.serializer_class = SubscriptionCreateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        serializer = SubscriptionSerializer(instance)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @transaction.atomic()
    def perform_create(self, serializer):
        instance = serializer.save()
        subscriber = instance.subscriber
        target = instance.target

        subscriber.subscriptions_count += 1
        subscriber.save(update_fields=["subscriptions_count"])
        target.subscribers_count += 1
        target.save(update_fields=["subscribers_count"])

        return instance

    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        subscriber = instance.subscriber
        target = instance.target

        subscriber.subscriptions_count -= 1
        subscriber.save(update_fields=["subscriptions_count"])
        target.subscribers_count -= 1
        target.save(update_fields=["subscribers_count"])

        return super().destroy(request, *args, **kwargs)
