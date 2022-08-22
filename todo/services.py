import random

from todo.models import Task


def _is_task_owner(request) -> bool:
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
