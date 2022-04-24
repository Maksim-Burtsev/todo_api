from dataclasses import field
from django.contrib import admin

from todo.models import Task, SubTask, ResetPasswordCode


class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'user', 'is_done')
    inlines = [SubTaskInline]

@admin.register(ResetPasswordCode)
class ResetPasswordCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'date_created', 'lasts_until')