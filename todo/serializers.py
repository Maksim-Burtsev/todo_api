from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from todo.mixins import CodeMixin
from todo.services import validate_and_decrement_reset_code
from todo.models import Task, SubTask, User, ResetPasswordCode


class DoneTasksSerializer(serializers.ModelSerializer):
    all_tasks = serializers.IntegerField()
    done = serializers.IntegerField()

    class Meta:
        model = User
        fields = ("all_tasks", "done")


class CreateNewPasswordSerializer(serializers.Serializer, CodeMixin):
    user_id = serializers.IntegerField()
    code = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    class Meta:
        fields = ("user_id", "code", "new_password", "confirm_password")

    def validate(self, data):
        user_id = data.get("user_id")
        code = data.get("code")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        validate_and_decrement_reset_code(user_id=user_id, user_code=code)

        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords don't match")

        if not ResetPasswordCode.objects.filter(code=code, user_id=user_id).exists():
            raise serializers.ValidationError("Uncorrect data")

        return super().validate(data)


class CodeSerializer(serializers.Serializer, CodeMixin):
    email = serializers.EmailField()
    code = serializers.CharField()

    class Meta:
        fields = (
            "email",
            "code",
        )

    def validate(self, data):
        email = data["email"]
        user_code = data["code"]

        user = get_object_or_404(User, email=email)

        validate_and_decrement_reset_code(user_id=user.id, user_code=user_code)

        return super().validate(data)


class EmailSerializer(serializers.Serializer):
    """
    Email для восстановления пароля
    """

    email = serializers.EmailField()

    class Meta:
        fields = ("email",)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email doesn't exists")
        return value


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Регистрация пользователя
    """

    username = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=55)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username already exists")
        return value

    class Meta:
        model = User
        fields = ("username", "email", "password")


class PasswordsSerializer(serializers.Serializer):
    """
    Обновление пароля
    """

    token = serializers.CharField()
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        token = data.get("token")
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        user = self.get_user(token)

        self.validate_passwords(user, old_password, new_password, confirm_password)

        return super().validate(data)

    @staticmethod
    def validate_passwords(
        user: User, old_password: str, new_password: str, confirm_password: str
    ) -> None:

        if not user.check_password(old_password):
            raise serializers.ValidationError("Old password incorrect!")

        if old_password == new_password:
            raise serializers.ValidationError("New password equal old!")

        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords don't match")

    @staticmethod
    def get_user(token: str) -> User:
        db_token = Token.objects.filter(key=token)

        if not db_token.exists():
            raise serializers.ValidationError("Invalid token")

        user = User.objects.get(id=db_token[0].user_id)

        return user


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ("id", "name", "description", "priority", "is_done")


class CreateSubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    week_number = serializers.IntegerField(read_only=True)
    overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "name",
            "description",
            "is_done",
            "priority",
            "date",
            "overdue",
            "user",
            "week_number",
            "subtasks",
        )
