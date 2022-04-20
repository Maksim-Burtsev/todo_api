from rest_framework import serializers

from todo.models import Task, SubTask, User


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ('id', 'name', 'description', 'priority', 'is_done')


class CreateSubTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubTask
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Task
        fields = ('id', 'name', 'description', 'is_done',
                  'priority', 'date', 'overdue', 'user', 'subtasks')
