import os
import random
from email.mime.text import MIMEText

import smtplib
from dotenv import load_dotenv

from todo.models import Task


def _is_task_owner(request):
    """Проверяет является ли создатель подзадачи владельцем задачи"""
    task_id = request.data.get('task')
    if task_id:
        task = Task.objects.get(id=task_id)
        if task.user != request.user:
            return False
    return True


def _generate_code() -> int:
    """
    Генерирует 5-ти значный код для восстановления пароля
    """
    code = f'{random.randint(1, 9)}'
    for _ in range(4):
        code += str(random.randint(0, 9))

    return int(code)


def send_code_on_email(code: int, user_email: str) -> None:
    """
    Отправляет код подтверждения на почту
    """

    load_dotenv()
    sender = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)

    message = MIMEText(f'{code}')
    message['Subject'] = 'Reset password'

    server.sendmail(sender, user_email, message.as_string())


if __name__ == '__main__':
    pass
