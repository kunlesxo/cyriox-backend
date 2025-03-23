from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserProfile
from .serializers import (
    UserSerializer,
    UserLoginSerializer,
    UserSignupSerializer,
    DistributorSignupSerializer,
    AdminSignupSerializer,
)



class AdminSignupView(APIView):
    def post(self, request):
        # Use the AdminSignupSerializer to create the new admin user
        serializer = AdminSignupSerializer(data=request.data)
        if serializer.is_valid():
            admin_user = serializer.save()  # Save the admin user
            return Response({"message": "Admin user created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            # Ensure that the user is an admin
            if user.role != "Admin":
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
    permission_classes = [IsAuthenticated, IsAdminUser]  # Only admins can access

    def get(self, request):
        """Retrieve all registered users"""
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

   
# 🚀 User (Customer) Signup
class SignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            UserProfile.objects.create(user=user)  # Create user profile
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🚀 Distributor Signup
class DistributorSignupView(APIView):
    def post(self, request):
        serializer = DistributorSignupSerializer(data=request.data)
        if serializer.is_valid():
            distributor = serializer.save()
            UserProfile.objects.create(user=distributor)  # Create distributor profile
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            login(request, user)

            # 🔹 Convert "base user" to "customer"
            role = user.role.lower().strip()
            if role == "base user":
                role = "customer"

            user_data = {
                "id": user.id,
                "username": user.username,
                "role": role,  # ✅ Now sending corrected role
                "email": user.email
            }

            return Response(
                {
                    "message": "Login successful",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "data": user_data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
