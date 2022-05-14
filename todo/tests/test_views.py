from cgitb import reset
import os
import json
from datetime import date
from black import read_pyproject_toml

from django.test import TestCase
from django.urls import reverse
from dotenv import load_dotenv

from rest_framework.authtoken.models import Token
from rest_framework import status


from todo.models import Task, SubTask, User, ResetPasswordCode


class TodoTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='test_user2',
            password='123ruFOJDvdspqw0id0f'
        )
        self.user_2 = User.objects.create_user(
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

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

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


class DoneTasksView(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='test_username',
            password='124Rrfdedqrq12',
            email='test@gmail.com',
        )

        for i in range(10):
            Task.objects.create(
                name=f'Test task{i}',
                user=self.user,
                date=date.today(),
            )
            Task.objects.create(
                name=f'Done Test task{i}',
                user=self.user,
                date=date.today(),
                is_done=True,
            )
            SubTask.objects.create(
                name=f'test subtask {i}',
                task_id=int((i+2)/2),
            )

        return super().setUp()

    def test_auth_case(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('done_tasks'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.dumps(response.data),
                         '[{"id": 1, "all_tasks": 35, "done": 12}]')

    def test_no_auth(self):

        response = self.client.get(reverse('done_tasks'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SubTaskTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='test_username',
            password='124Rrfdedqrq12',
            email='test@gmail.com',
        )

        self.user_2 = User.objects.create_user(
            username='test_2_username',
            password='12224Rrfdedqrq12',
            email='test2@gmail.com',
        )

        Task.objects.create(
            name=f'Done Test task',
            user=self.user,
            date=date.today(),
            is_done=True,
        )

        for i in range(10):
            subtask = SubTask.objects.create(
                name=f'test subtask{i}',
                task_id=1,
            )

        return super().setUp()

    def test_no_auth(self):
        response = self.client.get(reverse('subtask', args=(1,)))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_owner(self):
        self.client.force_login(self.user_2)

        response = self.client.get(reverse('subtask', args=(1,)))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner(self):
        self.client.force_login(self.user)

        response_1 = self.client.get(reverse('subtask', args=(1,)))
        response_2 = self.client.get(reverse('subtask', args=(7,)))

        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        self.assertEqual(response_2.status_code, status.HTTP_200_OK)

        self.assertEqual(response_1.data, {
                         'id': 1, 'name': 'test subtask0', 'description': None, 'priority': None, 'is_done': False})

        self.assertEqual(response_2.data, {
                         'id': 7, 'name': 'test subtask6', 'description': None, 'priority': None, 'is_done': False})

    def test_wrong_subtask(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('subtask', args=(8888,)))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreateSubtaskTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='FDwefewsa',
            password='124Rrfdede2dqrq12',
            email='d2r2sd@gmail.com',
        )

        self.user_2 = User.objects.create_user(
            username='FDEWSS2',
            password='124DSawqs',
            email='ASFS@gmail.com',
        )

        Task.objects.create(
            name=f'Test task',
            user=self.user,
            date=date.today(),
        )

        return super().setUp()

    def test_not_task_owner(self):
        self.client.force_login(self.user_2)

        response = self.client.post(reverse('create_subtask'), {
            "name": 'test subtask',
            "task": 1
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_is_task_owner(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('create_subtask'), {
            "name": 'test subtask',
            "task": 1
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(SubTask.objects.all().count(), 1)


class AuthenticationTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='admin',
            password='admin',
            email='admin@gmail.com',
        )
        return super().setUp()

    def test_auth(self):
        user = User.objects.create_user(
            username="test",
            password="test"
        )
        user.save()

        response = self.client.post(
            reverse('auth'), {"username": "test", "password": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)

    def test_register(self):

        response = self.client.post(reverse('register'), {
            'username': 'test_register',
            'password': '1244tfWDwa',
            'email': 'test@gmail.com'
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(User.objects.filter(
            username='test_register', email='test@gmail.com').exists())

    def test_update_password(self):

        Token.objects.create(user=self.user)

        response = self.client.post(reverse('update_password'), {
            'token': self.user.auth_token,
            'old_password': 'admin',
            'new_password': '123RWRWQRQ',
            'confirm_password': '123RWRWQRQ',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_send_code(self):
        load_dotenv()
        email = os.getenv('EMAIL')

        User.objects.create_user(
            username='test',
            password='test',
            email=email,
        )

        # response = self.client.post(reverse('send_code'), {'email':email})
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_email_send_code(self):

        response = self.client.post(reverse('send_code'),
                                    {'email': 'wrong_email@mail.ru'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_code(self):

        Token.objects.create(user=self.user)
        code = '12345'

        ResetPasswordCode.objects.create(
            user=self.user,
            code=code
        )

        response = self.client.post(reverse('check_code'), {
            'email': 'admin@gmail.com',
            'code': code
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'Correct': 'True', 'user_id': 1})

    def test_check_code_attempts(self):
        Token.objects.create(user=self.user)
        code = '12345'

        reset_code_obj = ResetPasswordCode.objects.create(
            user=self.user,
            code=code
        )

        for _ in range(5):
            response = self.client.post(reverse('check_code'), {
                'email': 'admin@gmail.com',
                'code': '54321'
            })
            self.assertEqual(response.status_code, 400)

        reset_code_obj.refresh_from_db()

        self.assertEqual(reset_code_obj.attempt, 0) 


    def test_create_password(self):

        Token.objects.create(user=self.user)
        code = '54321'

        ResetPasswordCode.objects.create(
            user=self.user,
            code=code
        )

        response = self.client.post(reverse('create_password'), {
            'user_id': self.user.id,
            'code': code,
            'new_password': '21dFEQEWqwds2',
            'confirm_password': '21dFEQEWqwds2'
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.check_password('21dFEQEWqwds2'))

    def test_create_password_attempts(self):

        Token.objects.create(user=self.user)
        code = '54321'

        reset_code = ResetPasswordCode.objects.create(
            user=self.user,
            code=code
        )

        response = self.client.post(reverse('create_password'), {
            'user_id': self.user.id,
            'code': '55555',
            'new_password': '21dFEQEWqwds2',
            'confirm_password': '21dFEQEWqwds2'
        })
        self.assertEqual(response.status_code, 400)

        reset_code.refresh_from_db()
        self.assertEqual(reset_code.attempt, 4)