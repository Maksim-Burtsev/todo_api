from django.urls import path, include

from rest_framework import routers

from todo.views import TodoViewSet

router = routers.SimpleRouter()
router.register(r'todo', TodoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
