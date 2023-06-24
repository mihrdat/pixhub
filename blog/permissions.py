from rest_framework import permissions
from .models import Author, Subscription


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.user


class HasAccessAuthorContent(permissions.BasePermission):
    def has_permission(self, request, view):
        current_author = request.user.author
        author = Author.objects.get(pk=view.kwargs["pk"])

        return bool(
            current_author == author
            or Subscription.objects.filter(
                subscriber=current_author, target=author
            ).exists()
            or not author.is_private
        )
