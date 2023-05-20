from django.core import exceptions
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "date_joined", "last_login", "is_active"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    jwt = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "password", "jwt"]

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs["password"]

        try:
            validate_password(password, user)
        except exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def get_jwt(self, user):
        refresh = RefreshToken.for_user(user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}
