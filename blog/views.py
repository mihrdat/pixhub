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
from django_filters.rest_framework import DjangoFilterBackend
from .models import Author, Subscription
from .serializers import AuthorSerializer, SubscriptionSerializer
from .permissions import IsSubscriberOrReadOnly
from .pagination import DefaultLimitOffsetPagination


class AuthorViewSet(
    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    queryset = Author.objects.select_related("user").all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            self.queryset = self.queryset.filter(user=user)
        return super().get_queryset()

    @action(methods=["GET", "PUT", "PATCH"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)

    def get_instance(self):
        return Author.objects.get(user=self.request.user)


class SubscriptionViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Subscription.objects.select_related("subscriber__user").all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsSubscriberOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["subscriber", "author"]
    pagination_class = DefaultLimitOffsetPagination
