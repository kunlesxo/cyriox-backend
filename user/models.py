import uuid
import pyotp
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class AppUserManager(BaseUserManager):
    def create_user(self, email, username, phone_number=None, role="Customer", password=None):
        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")

        user = self.model(
            id=uuid.uuid4(),
            email=self.normalize_email(email),
            username=username,
            phone_number=phone_number,
            role=role
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None):
        user = self.create_user(email=email, username=username, password=password, role="Admin")
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    class ROLE(models.TextChoices):
        CUSTOMER = "Customer", "Customer"
        DISTRIBUTOR = "Distributor", "Distributor"
        STAFF = "Staff", "Staff"
        ADMIN = "Admin", "Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    phone_number = models.CharField(max_length=14, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE.choices, default=ROLE.CUSTOMER)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ 2FA Fields
    two_factor_enabled = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=32, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = AppUserManager()

    def __str__(self):
        return f"{self.username} ({self.role})"

    def generate_otp_secret(self):
        """Generates a new OTP secret for 2FA"""
        self.otp_secret = pyotp.random_base32()
        self.save()

    def get_totp(self):
        """Returns a TOTP object using the user's OTP secret"""
        if self.otp_secret:
            return pyotp.TOTP(self.otp_secret)
        return None

# 🔹 Extended Profile Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    company_name = models.CharField(max_length=255, blank=True, null=True)  # For Distributors
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
