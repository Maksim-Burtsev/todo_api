from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, generics
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from todo.models import Task, SubTask, User
from todo.serializers import (
    TaskSerializer,
    SubTaskSerializer,
    CreateSubTaskSerializer,
    UserRegisterSerializer,
    PasswordsSerializer
)
from todo.permissions import IsOwner, IsTaskOwner
from todo.services import _is_task_owner


class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
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
        print(serializer.is_valid())
        if serializer.is_valid():
            user = User.objects.get(
                auth_token=serializer.validated_data['token'])
            user.set_password(serializer.validated_data['new_password'])
            user.save()
        # TODO обработать все ошибки
            print('nen ,skb')
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
