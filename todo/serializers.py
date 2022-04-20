from rest_framework import serializers

from todo.models import Task, SubTask


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

    class Meta:
        model = Task
        fields = ('name', 'description', 'is_done',
                  'priority', 'date', 'overdue', 'subtasks')
