import random

from django.utils import timezone
from django.db.models import F

from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework import status


from todo.models import Task, ResetPasswordCode


def validate_and_decrement_reset_code(
    user_id: int, user_code: ResetPasswordCode
) -> None:
    """
    Проверяет введённый пользователем код и уменьшает количество попыток на его правильное введение.
    """
    correct_code = _get_correct_user_code(user_id)
    _decrement_code_attempts(correct_code, user_code)


def _get_correct_user_code(user_id: int) -> ResetPasswordCode:
    """
    Достаёт из базы правильный (ожидаемый) код восстановления от пользователя
    """
    reset_password_code = ResetPasswordCode.objects.filter(user_id=user_id)
    if not reset_password_code.exists():
        raise serializers.ValidationError("Password wasn't reset")

    correct_code = reset_password_code[0]

    return correct_code


def _decrement_code_attempts(correct_code: ResetPasswordCode, user_code: int) -> None:
    """
    Уменьшает количество попыток (-1) на отправку кода восстановления пароля.
    Если код неправильный/попытки исчерпаны/код просрочен, то выбрасывается ошибка.
    """
    if correct_code.attempt == 0:
        raise APIException(
            detail="Attempts are over", status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    correct_code.attempt = F("attempt") - 1
    correct_code.save()

    if correct_code.code != user_code:
        raise serializers.ValidationError("Wrong code")

    if correct_code.lasts_until < timezone.now():
        raise serializers.ValidationError("Code is overdue")


def _is_task_owner(request) -> bool:
    """Проверяет является ли создатель подзадачи владельцем задачи"""
    task_id = request.data.get("task")
    if task_id:
        task = Task.objects.get(id=task_id)
        if task.user != request.user:
            return False
    return True


def _generate_code() -> int:
    """
    Генерирует 5-ти значный код для восстановления пароля
    """
    code = f"{random.randint(1, 9)}"
    for _ in range(4):
        code += str(random.randint(0, 9))

    return int(code)
