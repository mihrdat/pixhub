from rest_framework import permissions
from .models import Subscription


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.user


class HasAccessAuthorContent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        current_author = request.user.author
        return bool(
            current_author == obj
            or Subscription.objects.filter(
                subscriber=current_author, target=obj
            ).exists()
            or not obj.is_private
        )
