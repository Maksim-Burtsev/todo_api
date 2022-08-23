from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    message = "Not an owner"

    def has_object_permission(self, request, _, obj):
        return obj.user == request.user


class IsTaskOwner(permissions.BasePermission):
    message = "Not a task owner"

    def has_object_permission(self, request, _, obj):
        return obj.task.user == request.user
