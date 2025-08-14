from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse







class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must provide an email address.")
        email = self.normalize_email(email)

        # Remove M2M fields to avoid FK issues
        extra_fields.pop('groups', None)
        extra_fields.pop('user_permissions', None)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)







class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Add related_name to prevent reverse accessor clashes
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    



class Trial(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trial"
    )
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Check if trial is still valid."""
        return timezone.now() <= self.end_date

    def __str__(self):
        return f"Trial for {self.user.email} (ends {self.end_date.date()})"








