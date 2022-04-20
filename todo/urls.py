from django.urls import path, include

from rest_framework import routers

from todo.views import TodoViewSet, SubTaskDetailView, CreateSubTaskView

router = routers.SimpleRouter()
router.register('todo', TodoViewSet, basename='todo')

urlpatterns = [
    path('', include(router.urls)),
    path('subtask/<int:pk>/', SubTaskDetailView.as_view()),
    path('create_subtask/', CreateSubTaskView.as_view()),
]
