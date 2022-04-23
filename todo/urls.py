from django.urls import path, include

from rest_framework import routers
from rest_framework.authtoken import views

from todo.views import (
    TodoViewSet,
    SubTaskDetailView,
    CreateSubTaskView,
    RegisterUserView,
    UpdatePasswordView
)


router = routers.SimpleRouter()
router.register('todo', TodoViewSet, basename='todo')

urlpatterns = [
    path('api-token-auth/', views.obtain_auth_token),
    path('register/', RegisterUserView.as_view()),
    path('update_password/', UpdatePasswordView.as_view()),

    path('', include(router.urls)),

    path('subtask/<int:pk>/', SubTaskDetailView.as_view()),
    path('create_subtask/', CreateSubTaskView.as_view()),
]
