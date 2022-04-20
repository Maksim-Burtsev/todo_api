from datetime import date

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from todo.models import Task, SubTask, User
from todo.serializers import TaskSerializer


class TodoTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            username='test_user2',
            password='123ruFOJDvdspqw0id0f'
        )
        for i in range(10):
            Task.objects.create(
                name=f'Test task{i}',
                user=self.user,
                date=date.today(),
            )
            SubTask.objects.create(
                name=f'test subtask {i}',
                task_id=int((i+2)/2),
            )
        return super().setUp()

    def test_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('todo-list'))
        tasks = Task.objects.filter(user=self.user)
        serializer_data = TaskSerializer(tasks, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data, serializer_data)

    def test_nologin_get(self):
        response = self.client.get(reverse('todo-list'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('todo-list'), {
            "name": 'Test task111',
            "user_id": 1,
            "date": date.today()}
        )

        last_task = Task.objects.all().last()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(last_task.name, 'Test task111')
        self.assertEqual(last_task.user.id, 1)

    def test_update(self):
        pass
