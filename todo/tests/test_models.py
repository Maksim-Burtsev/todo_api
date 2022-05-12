import datetime
from datetime import date

from django.test import TestCase

from todo.models import (
    Task,
    SubTask,
    User,
    ResetPasswordCode
)


class TodoTasksTest(TestCase):

    def setUp(self) -> None:
        user = User.objects.create(
            username='test_user',
            password='123ruFOJDvdspqw0id0f'
        )
        return super().setUp()

    def test_Task(self):
        user = User.objects.get(pk=1)

        task_1 = Task.objects.create(
            name='Test task',
            user=user,
            date=date.today(),
        )
        task_2 = Task.objects.create(
            name='Test task 2',
            user=user,
            is_done=True,
            priority=1,
            date=date.today(),
        )
        task_3 = Task.objects.create(
            name='Test task 3',
            user=user,
            is_done=True,
            priority=1,
            date=date.today(),
        )

        self.assertEqual(Task.objects.all().count(), 3)

        self.assertEqual(task_1.date, date.today())
        self.assertFalse(task_1.is_done)

        self.assertTrue(task_2.is_done)
        self.assertEqual(task_2.priority, 1)


    def test_subtasks(self):
        user = User.objects.get(pk=1)

        task_1 = Task.objects.create(
            name='Test task',
            user=user,
            date=date.today(),
        )
        task_2 = Task.objects.create(
            name='Test task 2',
            user=user,
            is_done=True,
            priority=1,
            date=date.today(),
        )

        for i in range(10):
            SubTask.objects.create(
                name=f'test subtask {i}',
                task=task_1,
            )

        self.assertEqual(SubTask.objects.all().count(), 10)

        self.assertEqual(task_1.subtasks.all().count(), 10)

        self.assertEqual(task_2.subtasks.all().count(), 0)


class ResetPasswordCodeTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            username='Test_User123',
            email='test@gmail.com',
            password='21FEjdqwpowqu312wqa'
        )
        return super().setUp()

    def test_reset_pass_code(self):
        reset_code = ResetPasswordCode.objects.create(
            user_id=self.user.id,
            code='12345'
        )
        alive_time = reset_code.lasts_until-reset_code.date_created

        self.assertEqual(ResetPasswordCode.objects.all().count(), 1)

        self.assertEqual(reset_code.user.id, self.user.id)
        
        self.assertEqual(reset_code.code, '12345')

        self.assertEqual(alive_time, datetime.timedelta(seconds=300))
