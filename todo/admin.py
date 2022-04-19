from dataclasses import field
from django.contrib import admin

from todo.models import Task, SubTask


class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'user', 'is_done')
    inlines = [SubTaskInline]
