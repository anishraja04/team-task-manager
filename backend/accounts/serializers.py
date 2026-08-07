from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "name", "role", "created_at"]
        read_only_fields = ["id", "role", "created_at"]


class RegisterSerializer(serializers.ModelSerializer):
    # we do not want the password to be shown in any response
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)

    class Meta:
        model = User
        fields = ["id", "email", "username", "name", "password"]

    def validate_email(self, value):
        # two users should not have the same email
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        # we are using set_password so that it gets hashed and saved safely
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.email = user.email.lower()
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
