import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    def get_or_create_google_user(self, email, full_name, profile_picture):
        """Get or create a user from Google OAuth data"""
        try:
            user = self.get(email=email)
            # Update existing user with Google data if needed
            if user.auth_provider == 'google':
                if full_name and not user.full_name:
                    user.full_name = full_name
                if profile_picture and not user.profile_picture:
                    user.profile_picture = profile_picture
                user.save()
            return user, False
        except self.model.DoesNotExist:
            # Create new user with Google auth
            user = self.create_user(
                email=email,
                full_name=full_name,
                password=None,  # No password for Google users
                auth_provider='google',
                profile_picture=profile_picture,
                onboarding_completed=False,
                role='user',
                user_type='explorer'
            )
            return user, True

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('supervisor', 'Supervisor'),
        ('user', 'User'),
    ]

    USER_TYPE_CHOICES = [
        ('business_owner', 'Business Owner'),
        ('explorer', 'Explorer'),
    ]

    AUTH_PROVIDER_CHOICES = [
        ('local', 'Local'),
        ('google', 'Google'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, default='explorer')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='user')
    language = models.CharField(max_length=10, default='en')
    onboarding_completed = models.BooleanField(default=False)
    posts_generated = models.BooleanField(default=False)
    images_generated = models.BooleanField(default=False)
    auth_provider = models.CharField(max_length=20, choices=AUTH_PROVIDER_CHOICES, default='local')
    profile_picture = models.URLField(max_length=500, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
