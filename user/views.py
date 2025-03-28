import pyotp
import logging
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from .models import User, UserProfile
from .serializers import (
    UserSerializer,
    UserLoginSerializer,
    UserSignupSerializer,
    DistributorSignupSerializer,
    AdminSignupSerializer,
)
from .permissions import IsAdminUserCustom
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView


class CustomTokenRefreshView(TokenRefreshView):
    pass


class CustomTokenVerifyView(TokenVerifyView):
    pass


class AdminSignupView(APIView):
    def post(self, request):
        serializer = AdminSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Admin user created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            if user.role.lower() != "admin":
                return Response({"error": "Not authorized as admin"}, status=status.HTTP_403_FORBIDDEN)
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "Login successful",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user_id": user.id,
                    "username": user.username,
                    "role": user.role,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAllUsersView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get(self, request):
        users = User.objects.all()
        if not users.exists():
            return Response({"message": "No users found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(users, many=True)
        return Response(
            {"status": "success", "total_users": users.count(), "users": serializer.data},
            status=status.HTTP_200_OK,
        )


class SignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            UserProfile.objects.get_or_create(user=user)
            return Response({"message": "User registered successfully!", "user": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DistributorSignupView(APIView):
    def post(self, request):
        serializer = DistributorSignupSerializer(data=request.data)
        if serializer.is_valid():
            distributor = serializer.save()
            UserProfile.objects.get_or_create(user=distributor)
            return Response({"message": "Distributor registered successfully!", "distributor": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            if user.two_factor_enabled:
                totp = pyotp.TOTP(user.otp_secret)
                otp_code = totp.now()
                send_mail(
                    subject="Your 2FA Code",
                    message=f"Your OTP code is: {otp_code}",
                    from_email="noreply@cyriox.com",
                    recipient_list=[user.email],
                )
                return Response({"message": "OTP sent. Please verify before logging in."}, status=202)
            refresh = RefreshToken.for_user(user)
            login(request, user)
            return Response({
                "message": "Login successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role.lower(),
                    "email": user.email,
                },
            }, status=200)
        return Response(serializer.errors, status=400)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        otp_code = request.data.get("otp")

        if not check_password(old_password, user.password):
            return Response({"error": "Old password is incorrect"}, status=400)

        if user.two_factor_enabled:
            if not user.otp_secret:
                return Response({"error": "2FA is enabled but no OTP secret found"}, status=400)
            totp = pyotp.TOTP(user.otp_secret)
            if not totp.verify(otp_code):
                return Response({"error": "Invalid OTP"}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully!"}, status=200)

# ✅ Get User Details
class GetUserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response({"status": "success", "user": serializer.data}, status=status.HTTP_200_OK)


# ✅ Update User Profile
class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User profile updated successfully", "user": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Delete User Account
class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "User account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

logger = logging.getLogger(__name__)
# ✅ Send OTP for 2FA or Verification
class SendOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not user.otp_secret:
            user.otp_secret = pyotp.random_base32()
            user.save()

        totp = pyotp.TOTP(user.otp_secret)
        otp_code = totp.now()

        try:
            send_mail(
                subject="Your OTP Code",
                message=f"Your OTP code is: {otp_code}",
                from_email="noreply@cyriox.com",
                recipient_list=[user.email],
            )
            return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error sending OTP: {e}")  # 🔹 Log errors
            return Response({"error": "Failed to send OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ✅ Verify OTP for 2FA or Actions like Password Reset
class VerifyOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        otp_code = request.data.get("otp")

        if not otp_code:
            return Response({"error": "OTP code is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.otp_secret:
            return Response({"error": "No OTP secret found"}, status=status.HTTP_400_BAD_REQUEST)

        totp = pyotp.TOTP(user.otp_secret)
        if totp.verify(otp_code):
            return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)