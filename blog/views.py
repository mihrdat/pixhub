from django.db.models import Q
from django.db.models.aggregates import Count
from rest_framework import status
from rest_framework.response import Response
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Author, Article, Relation
from .serializers import (
    AuthorSerializer,
    ArticleSerializer,
    RelationSerializer,
)
from .permissions import IsOwnerOrReadOnly
from .pagination import DefaultLimitOffsetPagination


class AuthorViewSet(
    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    queryset = (
        Author.objects.select_related("user")
        .annotate(subscribers_count=Count("subscribers"))
        .annotate(subscriptions_count=Count("subscriptions"))
    )
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

    @action(methods=["POST"], detail=True)
    def subscribe(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=["DELETE"], detail=True)
    def unsubscribe(self, request, *args, **kwargs):
        try:
            Relation.objects.get(
                subscriber=self.request.user.author, target=self.kwargs["pk"]
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Relation.DoesNotExist:
            return Response(
                {
                    "detail": "Invalid unsubscription request! No existing subscription for the specified author."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def get_serializer_class(self):
        if self.action in ["subscribe", "unsubscribe"]:
            self.serializer_class = RelationSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        if self.action in ["subscribe", "unsubscribe"]:
            context = super().get_serializer_context()
            context["target"] = Author.objects.get(pk=self.kwargs["pk"])
            return context
        return super().get_serializer_context()

    def get_permissions(self):
        if self.action in ["subscribe", "unsubscribe"]:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_current_author(self):
        return super().get_queryset().get(user=self.request.user)


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = DefaultLimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["author"]

    def get_queryset(self):
        current_author = self.request.user.author
        subscriptions = current_author.subscriptions.values_list("target", flat=True)
        return (
            super()
            .get_queryset()
            .filter(Q(author_id__in=subscriptions) | Q(author_id=current_author.pk))
            .order_by("-created_at")
        )


class SubscriberViewSet(ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination
    filter_backends = [SearchFilter]
    search_fields = ["user__email"]

    def get_queryset(self):
        author = Author.objects.get(pk=self.kwargs["author_pk"])
        subscribers = author.subscribers.values_list("subscriber", flat=True)
        return super().get_queryset().filter(pk__in=subscribers)


class SubscriptionViewSet(ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination
    filter_backends = [SearchFilter]
    search_fields = ["user__email"]

    def get_queryset(self):
        author = Author.objects.get(pk=self.kwargs["author_pk"])
        subscriptions = author.subscriptions.values_list("target", flat=True)
        return super().get_queryset().filter(pk__in=subscriptions)
