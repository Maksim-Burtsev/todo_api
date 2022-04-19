from urllib import request
from rest_framework import viewsets

from todo.models import Task
from todo.serializers import TaskSerializer
from todo.permissions import IsOwner

class TodoViewSet(viewsets.ModelViewSet):

    serializer_class = TaskSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)