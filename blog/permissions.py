from rest_framework import permissions
from .models import Author, Subscription, Article


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(obj, Author):
            return request.user == obj.user

        elif isinstance(obj, Subscription):
            return request.user.author in [obj.subscriber, obj.target]

        elif isinstance(obj, Article):
            return request.user.author == obj.author


class IsSubscriberOrReadPublicOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        current_author = request.user.author
        author = Author.objects.get(pk=view.kwargs["author_pk"])

        return bool(
            current_author == author
            or Subscription.objects.filter(
                subscriber=current_author, target=author
            ).exists()
            or not author.is_private
        )
