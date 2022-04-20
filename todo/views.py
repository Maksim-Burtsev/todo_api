from rest_framework import viewsets, generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from todo.models import Task, SubTask
from todo.serializers import (
    TaskSerializer,
    SubTaskSerializer,
    CreateSubTaskSerializer
)
from todo.permissions import IsOwner, IsTaskOwner
from todo.services import _is_task_owner


class TodoViewSet(viewsets.ModelViewSet):

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated & IsOwner]

    def get_queryset(self):
        return Task.objects.filter(user_id=self.request.user)


class SubTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    permission_classes = [IsTaskOwner]


class CreateSubTaskView(generics.CreateAPIView):

    serializer_class = CreateSubTaskSerializer
    queryset = SubTask.objects.all()
    permission_classes = [IsTaskOwner]

    def post(self, request, *args, **kwargs):
        if not _is_task_owner(request):
            raise PermissionDenied(
                {"detail": "You don't have permission to access"})

        return super().post(request, *args, **kwargs)

            