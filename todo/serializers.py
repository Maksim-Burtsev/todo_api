from django import db
from rest_framework import serializers
from rest_framework.authtoken.models import Token


from todo.models import Task, SubTask, User


class UserRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=55)

    def validate_email(self, value):
        print(value)
        return value

    class Meta:
        model = User
        fields = ('username','email', 'password')
    

class PasswordsSerializer(serializers.Serializer):
    token = serializers.CharField()
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    comfirm_password = serializers.CharField()

    def validate(self, data):
        token = data.get('token')
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        comfirm_password = data.get('comfirm_password')

        db_token = Token.objects.filter(key=token)

        if not db_token.exists():
            raise serializers.ValidationError('Invalid token')

        user = User.objects.get(id=db_token[0].user_id)
        if not user.check_password(old_password):
            raise serializers.ValidationError('Old password incorrect!')

        if old_password == new_password:
            raise serializers.ValidationError('New password equal old!')

        if new_password != comfirm_password:
            raise serializers.ValidationError('Пароли не совпадают')

        return super().validate(data)


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ('id', 'name', 'description', 'priority', 'is_done')


class CreateSubTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubTask
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Task
        fields = ('id', 'name', 'description', 'is_done',
                  'priority', 'date', 'overdue', 'user', 'subtasks')
