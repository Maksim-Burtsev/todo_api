from rest_framework import serializers
from rest_framework.authtoken.models import Token


from todo.models import Task, SubTask, User


class CreateNewPasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    class Meta:
        fields = ('user_id', 'code', 'new_password', 'confirm_password')

    def validate(self, data):
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords don't match")

        return super().validate(data)


class CodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

    class Meta:
        fields = ('email', 'code',)

    def validate_code(self, value):
        if len(value) != 5:
            raise serializers.ValidationError('Wrong code')
        return value


class EmailSerializer(serializers.Serializer):
    """
    Email для восстановления пароля
    """
    email = serializers.EmailField()

    class Meta:
        fields = ('email',)

    def validate_email(self, value):
        # TODO есть ли email в базе данных
        return value


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Регистрация пользователя
    """
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=55)

    def validate_email(self, value):
        # TODO если email exists -> raise Exception
        return value

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class PasswordsSerializer(serializers.Serializer):
    """
    Обновление пароля
    """
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
            raise serializers.ValidationError("Passwords don't match")

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
