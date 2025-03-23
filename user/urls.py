from django.urls import path
from .views import (
    SignupView,
    LoginView,
    DistributorSignupView,
    GetAllUsersView,
    AdminSignupView,
    AdminLoginView

    
)

urlpatterns = [


    # Admin Signup
    path("signup/admin/", AdminSignupView.as_view(), name="admin-signup"),

    # Admin Login
    path("login/admin/", AdminLoginView.as_view(), name="admin-login"),
    # User Signup (Customer)
    path("signup/user/", SignupView.as_view(), name="signup-user"),

    # User Login
    path("login/", LoginView.as_view(), name="login"),

    path("users/", GetAllUsersView.as_view(), name="get-all-users"),


    # Distributor Signup
    path("signup/distributor/", DistributorSignupView.as_view(), name="signup-distributor"),

   
]
