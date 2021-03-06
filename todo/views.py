from django.utils import timezone
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
    DoneTasksSerializer
)
from todo.permissions import IsOwner, IsTaskOwner
from todo.services import _is_task_owner, _generate_code
from todo.tasks import send_code_on_email


class DoneTasksView(generics.ListAPIView):
    """
    Возвращает количество всех/выполненных задач пользователя
    """
    serializer_class = DoneTasksSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        done_tasks = Count('tasks', filter=Q(tasks__is_done=True))
        done_subtasks = Count('tasks', filter=Q(tasks__subtasks__is_done=True))

        return User.objects.filter(username=self.request.user) \
            .prefetch_related('tasks__subtasks') \
            .annotate(
            done_subtasks=done_subtasks,
            done_tasks=done_tasks,
            done=F('done_subtasks')+F('done_tasks'),
            all_tasks=Count('tasks')+Count('tasks__subtasks')
        )


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated & IsOwner]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filter_fields = ['is_done', 'priority', 'date', 'week_number']
    search_fields = ['name', 'description',
                     'subtasks__name', 'subtasks__description']

    def get_queryset(self):
        date_now = timezone.now().date()
        return Task.objects.filter(
            user_id=self.request.user
        ).annotate(
            overdue=ExpressionWrapper(
                Q(date__lt=date_now),
                output_field=BooleanField())
        ).prefetch_related('subtasks')


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
    permission_classes = [IsTaskOwner]

    def post(self, request, *args, **kwargs):
        if not _is_task_owner(request):
            raise PermissionDenied(
                {"detail": "You don't have permission to access"})

        return super().post(request, *args, **kwargs)


class CreateNewPasswordView(APIView):
    """
    Создание нового пароля после восстановления
    """
    def post(self, request):
        serializer = CreateNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data['user_id']
            code = serializer.data['code']
            new_password = serializer.data['new_password']

            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()

            user_token = Token.objects.filter(user_id=user.id)
            if user_token.exists():
                user_token[0].delete()

            ResetPasswordCode.objects.get(code=code, user_id=user_id).delete()

            return Response({'detail': 'Password created!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetCodeView(APIView):
    """
    Проверка кода
    """
    def post(self, request):
        serializer = CodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            user_id = User.objects.get(email=email).id

            return Response({
                'Correct': 'True',
                'user_id': user_id
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailView(APIView):
    """
    Отправка кода восстановления на почту
    """
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            code = _generate_code()
            send_code_on_email.delay(code, email)
            user = User.objects.get(email=email)
            reset_code, _ = ResetPasswordCode.objects.get_or_create(
                user=user,
            )
            reset_code.code = code
            reset_code.attempt = 5
            reset_code.save()
            return Response({
                'detail': 'Code on your email!'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterUserView(APIView):
    """
    Регистрация
    """
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            username = serializer.data['username']
            password = serializer.data['password']

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            token = Token.objects.create(user=user)
            return Response({
                'user': f'{user.username}',
                'token': f'{token}',
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordView(APIView):
    """
    Обновление пароля
    """
    def post(self, request):
        serializer = PasswordsSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(
                auth_token=serializer.validated_data['token'])
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                'detail': 'Password was changed!'
            })

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
