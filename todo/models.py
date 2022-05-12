import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from todo.validators import validate_code, validate_date


class ResetPasswordCode(models.Model):
    """
    Код подтверждения для восстановления пароля
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='code')

    code = models.CharField(max_length=10, validators=[validate_code, ])

    date_created = models.DateTimeField(blank=True, null=True)

    lasts_until = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs) -> None:
        self.date_created = timezone.now()
        self.lasts_until = self.date_created + \
            datetime.timedelta(seconds=(60*5))
        return super().save(*args, **kwargs)


class Task(models.Model):
    """Задание"""

    PRIORITY_CHOICE = (
        (1, 'green'),
        (2, 'yellow'),
        (3, 'red'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE, related_name='tasks', null=True)
    is_done = models.BooleanField(default=False)
    priority = models.PositiveSmallIntegerField(blank=True,
                                                null=True, choices=PRIORITY_CHOICE)
    date = models.DateField(validators=[validate_date])
    week_number = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.week_number = self.date.isocalendar().week
        return super().save(*args, **kwargs)


class SubTask(models.Model):
    """Подзадание"""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=255, blank=True,
                                null=True, choices=Task.PRIORITY_CHOICE)
    is_done = models.BooleanField(default=False)
    task = models.ForeignKey(Task,
                             on_delete=models.CASCADE,                    related_name='subtasks')
