from rest_framework import status
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


# TODO кастомизировать сообщение в письме

class CreateNewPasswordView(APIView):
    def post(self, request):
        serializer = CreateNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.data['user_id']
            code = serializer.data['code']
            new_password = serializer.data['new_password']
            
            reset_code = ResetPasswordCode.objects.filter(code=code, user_id=user_id)
            if not reset_code.exists():
                return Response({'detail': 'Bad request'})

            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()

            user_token = Token.objects.filter(user_id=user.id)
            if user_token.exists():
                user_token[0].delete()

            reset_code[0].delete()

            return Response({'detail': 'Password created!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetCodeView(APIView):
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
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
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
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.save()  # TODO вот это лишнее скорее всего
            user, _ = User.objects.get_or_create(
                username=serializer.data['username'])
            # TODO если пользователь уже есть, то сразу возвращать ответ
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': f'{user.username}',
                'token': f'{token}',
            }, status=status.HTTP_201_CREATED)

        return Response({'detail': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordView(APIView):
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
        return Response({
            'detail': 'Invalid data!'
        }, status=status.HTTP_400_BAD_REQUEST)


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
