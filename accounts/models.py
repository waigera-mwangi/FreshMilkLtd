from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings


# -------------------
# Custom Manager
# -------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError(_('The Username field is required'))
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(username, email, password, **extra_fields)


# -------------------
# Custom Phone Field
# -------------------
class CustomPhoneNumberField(PhoneNumberField):
    default_error_messages = {
        'Invalid': 'Please enter a valid phone number in the format +254700000000'
    }


# -------------------
# Abstract Timestamp
# -------------------
class TimeStamp(models.Model):
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


# -------------------
# Custom User Model
# -------------------
from django.utils.crypto import get_random_string

class User(AbstractUser):
    class UserTypes(models.TextChoices):
        FARMER = 'FR', _('Farmer')
        FINANCE_MANAGER = 'FM', _('Finance Manager')
        FIELD_AGENT = 'FA', _('Field Agent')
        FIELD_MANAGER = 'FD', _('Field Manager')
        VETERINARY_OFFICER = 'VO', _('Veterinary Officer')
        ADMIN = 'AD', _('Admin')

    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = CustomPhoneNumberField(unique=True, null=True)
    user_type = models.CharField(max_length=2, choices=UserTypes.choices, default=UserTypes.FARMER)
    farmer_id = models.CharField(max_length=10, unique=True, null=True, blank=True)  # NEW FIELD
    town = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_user_type_display(self):
        return dict(User.UserTypes.choices).get(self.user_type, "Unknown")

    def save(self, *args, **kwargs):
        if self.username:
            self.username = self.username.lower()
        
        # Auto-generate Farmer ID for Farmers if not set
        if self.user_type == self.UserTypes.FARMER and not self.farmer_id:
            self.farmer_id = self.generate_farmer_id()
        
        super().save(*args, **kwargs)

    def generate_farmer_id(self):
        """Generate a unique Farmer ID like FRM12345"""
        while True:
            new_id = get_random_string(5, allowed_chars='0123456789')  # numeric only
            if not User.objects.filter(farmer_id=new_id).exists():
                return new_id

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


# -------------------
# Base Profile Model
# -------------------
class Profile(TimeStamp):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='Users/profile_pictures/%Y/%m/', default="null")
    phone_number = CustomPhoneNumberField(null=False)
    town = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    gender = models.CharField(
        max_length=1,
        choices=[('M', _('Male')), ('F', _('Female')), ('O', _('Other'))],
        default='M'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


# -------------------
# Specific Profiles
# -------------------
class FarmerProfile(Profile):
    class Meta:
        verbose_name = 'Farmer Profile'
        verbose_name_plural = 'Farmer Profiles'


class FinanceProfile(Profile):
    class Meta:
        verbose_name = 'Finance Profile'
        verbose_name_plural = 'Finance Profiles'


class FieldProfile(Profile):
    class Meta:
        verbose_name = 'Field Agent Profile'
        verbose_name_plural = 'Field Agent Profiles'


class ManagerProfile(Profile):
    class Meta:
        verbose_name = 'Field Manager Profile'
        verbose_name_plural = 'Field Manager Profiles'


class VeterinaryProfile(Profile):
    class Meta:
        verbose_name = 'Veterinary Profile'
        verbose_name_plural = 'Veterinary Profiles'
