from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, F, ExpressionWrapper, BooleanField

from rest_framework import status
from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.filters import SearchFilter

from django_filters.rest_framework.backends import DjangoFilterBackend

from todo.models import Task, SubTask, User, ResetPasswordCode
from todo.serializers import (
    TaskSerializer,
    SubTaskSerializer,
    CreateSubTaskSerializer,
    UserRegisterSerializer,
    PasswordsSerializer,
    EmailSerializer,
    CodeSerializer,
    CreateNewPasswordSerializer,
    DoneTasksSerializer,
)
from todo.permissions import IsOwner, IsTaskOwner
from todo.services import is_task_owner, generate_code
from todo.tasks import send_code_on_email


class DoneTasksView(generics.ListAPIView):
    """
    Возвращает количество всех/выполненных задач пользователя
    """

    serializer_class = DoneTasksSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        done_tasks = Count("tasks", filter=Q(tasks__is_done=True))
        done_subtasks = Count("tasks", filter=Q(tasks__subtasks__is_done=True))

        return (
            User.objects.filter(username=self.request.user)
            .prefetch_related("tasks__subtasks")
            .annotate(
                done_subtasks=done_subtasks,
                done_tasks=done_tasks,
                done=F("done_subtasks") + F("done_tasks"),
                all_tasks=Count("tasks") + Count("tasks__subtasks"),
            )
        )


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated & IsOwner]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filter_fields = ["is_done", "priority", "date", "week_number"]
    search_fields = ["name", "description", "subtasks__name", "subtasks__description"]

    def get_queryset(self):
        date_now = timezone.now().date()
        return (
            Task.objects.filter(user_id=self.request.user)
            .annotate(
                overdue=ExpressionWrapper(
                    Q(date__lt=date_now), output_field=BooleanField()
                )
            )
            .prefetch_related("subtasks")
        )

    def perform_update(self, serializer):
        # если задача становится выполненной, то все подзадачи выполняются автоматически
        if "is_done" in serializer.validated_data:
            if serializer.validated_data["is_done"] and not serializer.instance.is_done:
                serializer.instance.subtasks.update(is_done=True)
        return super().perform_update(serializer)


class SubTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Подзадача
    """

    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    permission_classes = [IsTaskOwner]


class CreateSubTaskView(generics.CreateAPIView):
    """
    Создание подзадачи
    """

    serializer_class = CreateSubTaskSerializer
    queryset = SubTask.objects.all()

    def post(self, request, *args, **kwargs):
        if not is_task_owner(request):
            raise PermissionDenied({"detail": "You don't have permission to access"})

        return super().post(request, *args, **kwargs)


class CreateNewPasswordView(APIView):
    """
    Создание нового пароля после восстановления
    """

    def post(self, request):
        serializer = CreateNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data["user_id"]
            code = serializer.data["code"]
            new_password = serializer.data["new_password"]

            self.update_password(user_id, new_password)
            self.delete_token(user_id)

            ResetPasswordCode.objects.get(code=code, user_id=user_id).delete()

            return Response(
                {"detail": "Password created!"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def update_password(user_id: int, new_password: str) -> None:
        """
        Обновляет пароль пользователя с указанным id
        """
        user = get_object_or_404(User, id=user_id)
        user.set_password(new_password)
        user.save()

    @staticmethod
    def delete_token(user_id: int) -> None:
        """
        Удаляет токен авторизации, если он существует
        """
        user_token = Token.objects.filter(user_id=user_id)
        if user_token.exists():
            user_token[0].delete()


class GetCodeView(APIView):
    """
    Проверка кода
    """

    def post(self, request):
        serializer = CodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data["email"]
            user = get_object_or_404(User, email=email)

            return Response(
                {"Correct": "True", "user_id": user.id}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailView(APIView):
    """
    Отправка кода восстановления на почту
    """

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data["email"]
            code = generate_code()
            send_code_on_email.delay(code, email)

            self.save_code_in_db(email, code)
            return Response(
                {"detail": "Code on your email!"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def save_code_in_db(email: str, code: int) -> None:
        """
        Сохраняет код восстановления пароля в базу.

        *5 - количество попыток на введение правильного кода.

        Если в базе есть предыдущий код восстановления для пользователя, то он **обновляется** и вместе с тем обновляются попытки.
        """
        user = get_object_or_404(User, email=email)
        reset_code, created = ResetPasswordCode.objects.get_or_create(user=user)
        reset_code.code = code
        if not created:
            reset_code.attempt = 5
        reset_code.save()


class RegisterUserView(APIView):
    """
    Регистрация
    """

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data["email"]
            username = serializer.data["username"]
            password = serializer.data["password"]

            user = User.objects.create_user(
                username=username, email=email, password=password
            )
            token = Token.objects.create(user=user)
            return Response(
                {
                    "user": f"{user.username}",
                    "token": f"{token}",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordView(APIView):
    """
    Обновление пароля
    """

    def post(self, request):
        serializer = PasswordsSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(
                User, auth_token=serializer.validated_data["token"]
            )
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"detail": "Password was changed!"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
