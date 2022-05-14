from datetime import date

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import F

from rest_framework import serializers


def _validate_and_update_reset_code(user_id, code):
    """
    Валидирует код восстановления и уменьшает количество попыток 
    """
    from todo.models import ResetPasswordCode

    reset_password_code = ResetPasswordCode.objects.filter(user_id=user_id)
    if not reset_password_code.exists():
        raise serializers.ValidationError("Password wasn't reset")

    reset_code_obj = reset_password_code[0]
    if reset_code_obj.attempt == 0:
        raise serializers.ValidationError("Attempts are over")

    reset_code_obj.attempt = F('attempt') - 1
    reset_code_obj.save()

    if reset_code_obj.code != code:
        raise serializers.ValidationError("Wrong code")

    if reset_code_obj.lasts_until < timezone.now():
        raise serializers.ValidationError("Code is overdue")

    return reset_code_obj



def validate_attempt(value: int):
    if not 0 <= value <= 5:
        raise ValidationError('Number of attempts must be between 0 and 5')
    return value


def validate_code(value: str):
    if len(value) != 5:
        raise ValidationError('Length of code must be five')
    if not value.isdigit():
        raise ValidationError('Code must be digit')

    return value


def validate_date(task_date):
    if task_date < date.today():
        raise ValidationError('Date can only be current or future!')
