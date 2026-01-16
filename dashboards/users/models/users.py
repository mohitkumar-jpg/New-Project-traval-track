from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        return self.create_user(
            email=email,
            password=password,
            user_type="super_admin",
            is_staff=True,
            is_superuser=True,
        )


class User(AbstractBaseUser, PermissionsMixin):

    USER_TYPES = (
        ("super_admin", "Super Admin"),
        ("branch_user", "Branch User"),
        ("client_user", "Client User"),
    )

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # 🔐 REFRESH TOKEN (SQL)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    refresh_token_expiry = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    # --------------------
    # Refresh Token Helpers
    # --------------------
    def set_refresh_token(self, token, days=1):
        self.refresh_token = token
        self.refresh_token_expiry = timezone.now() + timedelta(days=days)
        self.save(update_fields=["refresh_token", "refresh_token_expiry"])

    def is_refresh_token_valid(self, token):
        if not self.refresh_token or not self.refresh_token_expiry:
            return False
        if self.refresh_token != token:
            return False
        return timezone.now() < self.refresh_token_expiry

    def clear_refresh_token(self):
        self.refresh_token = None
        self.refresh_token_expiry = None
        self.save(update_fields=["refresh_token", "refresh_token_expiry"])

    def __str__(self):
        return self.email
