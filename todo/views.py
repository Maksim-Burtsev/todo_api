from rest_framework import viewsets

from todo.models import Task
from todo.serializers import TaskSerializer


class TodoViewSet(viewsets.ModelViewSet):

    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all()