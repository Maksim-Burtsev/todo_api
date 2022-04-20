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
        #TODO вынести валидацию
        task_id = request.data['task']
        task = Task.objects.get(id=task_id)
        if task.user != request.user:
            raise PermissionDenied(
                {"detail": "You don't have permission to access"})
        return super().post(request, *args, **kwargs)
