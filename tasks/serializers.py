from rest_framework import serializers
from .models import Task
from django.contrib.auth.models import User


class TaskSerializer(serializers.ModelSerializer):

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError(
                "Title must be at least 5 characters long."
            )

        return value

    def validate(self, data):
        completed = data.get(
            'completed',
            self.instance.completed if self.instance else False
        )

        description = data.get(
            'description',
            self.instance.description if self.instance else ''
        )

        if completed and len(description) < 10:
            raise serializers.ValidationError(
                "Completed tasks must have a description of at least 10 characters."
            )

        return data

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'completed']
        read_only_fields = ['id', 'owner']


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user