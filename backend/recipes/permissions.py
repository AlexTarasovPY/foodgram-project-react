from rest_framework import permissions


class OwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in (
                'POST', 'PATCH', 'DELETE'
            ) and request.user.is_authenticated
        ) or request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        if request.method == "POST" and request.user.is_authenticated:
            return True
        else:
            return (
                request.method in permissions.SAFE_METHODS
                or obj.author == request.user
            )
