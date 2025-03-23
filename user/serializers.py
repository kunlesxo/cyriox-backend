from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

from django.contrib.auth import get_user_model

User = get_user_model()



class AdminSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            role="Admin"  # Set the role to "Admin"
        )
        return user
# 🚀 User Serializer (General)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "role", "phone_number", "is_active"]


# 🚀 User Signup Serializer (Base User / Customer)
class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            role="Base User"  # Default role for customers
        )
        return user


# 🚀 Distributor Signup Serializer
class DistributorSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        distributor = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            role="Distributor"  # Set role as Distributor
        )
        return distributor



# 🚀 User Login Serializer
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        data["user"] = user
        return data


