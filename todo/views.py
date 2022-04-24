from django.utils import timezone

from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from todo.models import Task, SubTask, User, ResetPasswordCode
from todo.serializers import (
    TaskSerializer,
    SubTaskSerializer,
    CreateSubTaskSerializer,
    UserRegisterSerializer,
    PasswordsSerializer,
    EmailSerializer,
    CodeSerializer,
    CreateNewPasswordSerializer
)
from todo.permissions import IsOwner, IsTaskOwner
from todo.services import _is_task_owner, send_code_on_email, _generate_code


# TODO обработать случай, когда данные из сериалайзера не валидные
# TODO добавить status-коды

class CreateNewPasswordView(APIView):
    def post(self, request):
        serializer = CreateNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data['user_id']
            code = serializer.data['code']
            new_password = serializer.data['new_password']

            if not ResetPasswordCode.objects.filter(code=code, user_id=user_id).exists():
                return Response({'detail': 'Bad request'})

            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()

            user_token = Token.objects.filter(user_id=user.id)
            if user_token.exists():
                user_token[0].delete()

            return Response({'detail': 'Password created!'})


class GetCodeView(APIView):
    def post(self, request):
        serializer = CodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            code = serializer.data['code']

            user = User.objects.get(email=email)
            reset_password_code = ResetPasswordCode.objects.filter(
                code=code, user_id=user.id)

            if not reset_password_code.exists():
                return Response({'detail': 'Bad request'})
            reset_code = reset_password_code[0]

            if reset_code.lasts_until < timezone.now():
                return Response({'detail': 'Code was overdue'})
            return Response({
                'Correct': 'True',
                'user_id': user.id
            })


class EmailView(APIView):
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            # TODO кастомизировать сообщение в письме
            code = _generate_code()
            send_code_on_email(code, email)
            user = User.objects.get(email=email)
            reset_code, _ = ResetPasswordCode.objects.get_or_create(
                user=user,
            )
            reset_code.code = code
            reset_code.save()
            return Response({
                'detail': 'Code on your email!'
            })
        return Response({'detail': 'Bad request'})


class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # TODO вот это лишнее скорее всего
            user, _ = User.objects.get_or_create(
                username=serializer.data['username'])
            # TODO если пользователь уже есть, то сразу возвращать ответ
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': f'{user.username}',
                'token': f'{token}',
            })

        return Response({'detail': 'Bad request'})


class UpdatePasswordView(APIView):
    def post(self, request):
        serializer = PasswordsSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(
                auth_token=serializer.validated_data['token'])
            user.set_password(serializer.validated_data['new_password'])
            user.save()
        # TODO обработать все ошибки
            return Response({
                'detail': 'Password was changed!'
            })
        return Response({
            'detail': 'Invalid data!'
        })


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated & IsOwner]

    def get_queryset(self):
        return Task.objects.filter(user_id=self.request.user)


class SubTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    permission_classes = [IsTaskOwner]


class CreateSubTaskView(generics.CreateAPIView):

    serializer_class = CreateSubTaskSerializer
    queryset = SubTask.objects.all()
    permission_classes = [IsTaskOwner]

    def post(self, request, *args, **kwargs):
        if not _is_task_owner(request):
            raise PermissionDenied(
                {"detail": "You don't have permission to access"})

        return super().post(request, *args, **kwargs)
