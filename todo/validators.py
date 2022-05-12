from datetime import date

from django.core.exceptions import ValidationError


def validate_code(value: str):
    if len(value) != 5:
        raise ValidationError('Length of code must be five')
    if not value.isdigit():
        raise ValidationError('Code must be digit')

    return value


def validate_date(task_date):
    if task_date < date.today():
        raise ValidationError('Date can only be current or future!')
