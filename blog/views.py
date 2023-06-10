from django.db.models.aggregates import Count
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from .models import Author, Article
from .serializers import (
    AuthorSerializer,
    ArticleSerializer,
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
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)

    def get_object(self):
        if self.action == "me":
            return super().get_queryset().get(user=self.request.user)
        return super().get_object()


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
        author_pk = self.kwargs["author_pk"]
        if author_pk == "me":
            author_pk = self.request.user.author.pk
        return super().get_queryset().filter(author_id=author_pk)
