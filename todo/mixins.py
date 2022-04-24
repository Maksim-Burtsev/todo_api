from rest_framework import serializers


class CodeMixin:
    def validate_code(self, value):
        if len(value) != 5:
            raise serializers.ValidationError('Wrong code')
        return value