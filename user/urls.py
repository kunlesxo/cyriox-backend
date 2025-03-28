from django.urls import path
from .views import (
    SignupView,
    LoginView,
    DistributorSignupView,
    GetAllUsersView,
    AdminSignupView,
    AdminLoginView,
    LogoutView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    GetUserDetailView,
    UpdateUserView,
    DeleteUserView,
    SendOTPView,
    VerifyOTPView,
    ChangePasswordView
)

urlpatterns = [
    # 🔹 Admin Authentication
    path("admin/signup/", AdminSignupView.as_view(), name="admin-signup"),
    path("admin/login/", AdminLoginView.as_view(), name="admin-login"),

    # 🔹 User Authentication
    path("user/signup/", SignupView.as_view(), name="user-signup"),
    path("user/login/", LoginView.as_view(), name="user-login"),
    path("distributor/signup/", DistributorSignupView.as_view(), name="distributor-signup"),
    path("logout/", LogoutView.as_view(), name="logout"),
    
    # 🔹 JWT Token Management
    path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    path("auth/token/verify/", CustomTokenVerifyView.as_view(), name="token-verify"),

    # 🔹 User Management
    path("users/", GetAllUsersView.as_view(), name="get-all-users"),
    path("users/<uuid:user_id>/", GetUserDetailView.as_view(), name="get-user-detail"),
    path("users/<uuid:user_id>/update/", UpdateUserView.as_view(), name="update-user"),
    path("users/<uuid:user_id>/delete/", DeleteUserView.as_view(), name="delete-user"),
    path("users/change-password/", ChangePasswordView.as_view(), name="change-password"),

    # 🔹 Two-Factor Authentication (2FA)
    path("2fa/send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("2fa/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
]
