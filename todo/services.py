from todo.models import Task


def _is_task_owner(request):
    """Проверяет является ли создатель подзадачи владельцем задачи"""
    task_id = request.data.get('task')
    if task_id:
        task = Task.objects.get(id=task_id)
        if task.user != request.user:
            return False
    return True
