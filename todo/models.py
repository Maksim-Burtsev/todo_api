from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    """Задание"""

    # TODO время выполнения
    PRIORITY_CHOICE = (
        (1, 'green'),
        (2, 'yellow'),
        (3, 'red'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE, related_name='tasks')
    is_done = models.BooleanField(default=False)
    priority = models.PositiveSmallIntegerField(blank=True,
                                null=True, choices=PRIORITY_CHOICE)
    date = models.DateField()
    overdue = models.BooleanField(blank=True, null=True, default=False)

    def __str__(self) -> str:
        return self.name


class SubTask(models.Model):
    """Подзадание"""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=255, blank=True,
                                null=True, choices=Task.PRIORITY_CHOICE)
    is_done = models.BooleanField(default=False)
    task = models.ForeignKey(Task,
                             on_delete=models.CASCADE,                    related_name='subtasks')
