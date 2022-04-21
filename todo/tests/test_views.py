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
        self.user_2 = User.objects.create(
            username='test_user_2_0',
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
        self.client.force_login(self.user)
        self.task = Task.objects.get(pk=1)

        url = reverse('todo-detail', args=(self.task.id,))
        test_date = date.today()
        data = {
            'id': 1,
            'name': 'Updated name',
            'date': test_date
        }

        response = self.client.put(url, data, content_type='application/json')
        self.task.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.task.name, 'Updated name')
        self.assertEqual(self.task.date, test_date)

    def test_delete(self):
        self.client.force_login(self.user)
        self.task = Task.objects.get(pk=1)

        tasks_count = Task.objects.all().count()
        url = reverse('todo-detail', args=(self.task.id,))

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.all().count(), tasks_count-1)

    def test_delete_not_owner(self):

        self.task = Task.objects.get(pk=3)

        self.client.force_login(self.user_2)

        url = reverse('todo-detail', args=(self.task.id,))

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_not_owner(self):
        self.client.force_login(self.user_2)
        self.task = Task.objects.get(pk=1)

        url = reverse('todo-detail', args=(self.task.id,))
        test_date = date.today()
        data = {
            'id': 1,
            'name': 'Updated name',
            'date': test_date
        }

        response = self.client.put(url, data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_detail(self):
        self.client.force_login(self.user)
        self.task = Task.objects.get(pk=1)

        url = reverse('todo-detail', args=(self.task.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), self.task.id)

    def test_get_detail_not_owner(self):
        self.client.force_login(self.user_2)
        self.task = Task.objects.get(pk=1)

        url = reverse('todo-detail', args=(self.task.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)