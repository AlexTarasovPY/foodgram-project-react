from rest_framework import permissions


class OwnerOrReadOnly(permissions.BasePermission):
    """
    кастомный класс permission,
    позволяет редактировать/удалять рецепт только автору,
    оставляя остальным пользователям права на чтение.
    Авторизованный пользовательможет создавать рецепт.
    """

    def has_permission(self, request, view):
        return (
            request.method not in permissions.SAFE_METHODS and
            request.user.is_authenticated
        ) or request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return ((request.method == "POST" and request.user.is_authenticated) or
                request.method in permissions.SAFE_METHODS or
                obj.author == request.user)
