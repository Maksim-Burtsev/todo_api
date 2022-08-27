from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    message = "Not an owner"

    def has_object_permission(self, request, _, obj):
        return obj.user == request.user


class IsTaskOwner(permissions.BasePermission):
    """Является ли пользователем задачи к которой он хочет добавить подзадачу"""

    message = "Not a task owner"

    def has_object_permission(self, request, _, obj):
        return obj.task.user == request.user
