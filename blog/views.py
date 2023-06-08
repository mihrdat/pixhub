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
from .models import Author, Relation, Article
from .serializers import (
    AuthorSerializer,
    RelationSerializer,
    ArticleSerializer,
)
from .permissions import IsSubscriberOrReadOnly, IsOwnerOrReadOnly
from .pagination import DefaultLimitOffsetPagination


class AuthorViewSet(
    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    queryset = Author.objects.select_related("user").all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination
    filter_backends = [SearchFilter]
    search_fields = ["user__email"]

    @action(methods=["GET", "PUT", "PATCH"], detail=False)
    def me(self, request, *args, **kwargs):
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)

    def get_object(self):
        if self.action == "me":
            return Author.objects.get(user=self.request.user)
        return super().get_object()


class RelationViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
    permission_classes = [IsAuthenticated, IsSubscriberOrReadOnly]
    pagination_class = DefaultLimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["subscriber", "target"]


class ArticleViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
    GenericViewSet,
):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        return super().get_queryset().filter(author=self.kwargs["author_pk"])
