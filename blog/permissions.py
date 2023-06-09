from rest_framework import permissions
from .models import Author, Article


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if isinstance(obj, Author):
            return obj.user == request.user
        elif isinstance(obj, Article):
            return obj.author == request.user.author
