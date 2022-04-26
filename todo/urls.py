from django.urls import path, include

from rest_framework import routers
from rest_framework.authtoken import views

from todo.views import (
    TodoViewSet,
    SubTaskDetailView,
    CreateSubTaskView,
    RegisterUserView,
    UpdatePasswordView,
    EmailView,
    GetCodeView,
    CreateNewPasswordView,
    DoneTasksView
)


router = routers.SimpleRouter()
router.register('todo', TodoViewSet, basename='todo')

urlpatterns = [
    path('', include(router.urls)),

    path('api-token-auth/', views.obtain_auth_token, name='auth'),
    path('register/', RegisterUserView.as_view()),
    path('update_password/', UpdatePasswordView.as_view()),
    path('send_codе/', EmailView.as_view()),
    path('check_code/', GetCodeView.as_view()),
    path('create_password/', CreateNewPasswordView.as_view()),

    path('subtask/<int:pk>/', SubTaskDetailView.as_view(), name='subtask'),
    path('create_subtask/', CreateSubTaskView.as_view(), name='create_subtask'),
    path('done_tasks/', DoneTasksView.as_view(),name='done_tasks')
]
