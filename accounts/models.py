from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

class CustomPhoneNumberField(PhoneNumberField):
    default_error_messages = {
        'Invalid': 'Please enter a valid phone number in the format +254700000000'
    }
  
class TimeStamp(models.Model):
    updated = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True
        
        
class User(AbstractUser, PermissionsMixin):
    class UserTypes(models.TextChoices):
        FARMER = 'FR', _('FARMER')
        FINANCE_MANAGER = 'FM', _('FINANCE MANAGER')
        FIELD_AGENT = 'FA', _('FIELD AGENT')
        FIELD_MANAGER = 'FD', _('FIELD MANAGER')
        VETERINARY_OFFICER = 'VO', _('VETERINARY OFFICER')
        ADMIN = 'AD', _('ADMIN')
        
    user_type = models.CharField(
        max_length=2,
        choices = UserTypes.choices,
        default=UserTypes.CUSTOMER,
    )
    first_name = models.CharField( max_length=250)
    last_name = models.CharField( max_length=250)
    phone_number = CustomPhoneNumberField(unique=True, null=True)
    town = models.CharField(max_length=20)
    location = models.CharField(max_length=20)
    is_active = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    updated = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)

    def get_user_type_display(self):
        return dict(User.UserTypes.choices)[self.user_type]


    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

# profiles
class Profile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        OTHER = 'O', _('Other')

    image = models.ImageField(upload_to='Users/profile_pictures/%Y/%m/',
                              default="null")
    phone_number = CustomPhoneNumberField(null=False)
    town = models.CharField(max_length=20)
    location = models.CharField(max_length=20)
    is_active = models.BooleanField(_('Active'), default=True, help_text=_('Activated, users profile is published'))
    updated = models.DateField(_('Updated'), auto_now=True)
    created = models.DateField(_('Created'), auto_now_add=True)
    gender = models.CharField(
        max_length=2,
        choices=Gender.choices,
        default=Gender.MALE,
    )
    
# farmer
class FarmerProfile(Profile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')

    class Meta:
        verbose_name = 'Farmer Profile'
        verbose_name_plural = 'Farmer Profile'
        
# finance manager
class FinanceProfile(Profile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='finance_profile')

    class Meta:
        verbose_name = 'Finance Profile'
        verbose_name_plural = 'Finance Profile'
# Field Agent
class FieldProfile(Profile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='field_agent_profile')

    class Meta:
        verbose_name = 'Field Agent Profile'
        verbose_name_plural = 'Field Agent Profile'

# manager
class ManagerProfile(Profile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='field_manager_profile')

    class Meta:
        verbose_name = 'Field Manager Profile'
        verbose_name_plural = 'Field Manager Profile'
        
#  veterinary
class VeterinaryProfile(Profile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='veterinary_profile')

    class Meta:
        verbose_name = 'Veterinary Profile'
        verbose_name_plural = 'Veterinary Profile'
        


class Farmer(User):
    pass

    class Meta:
        verbose_name = 'Farmer'
        verbose_name_plural = 'Farmers'
        
class Finance(User):
    pass

    class Meta:
        verbose_name = 'Finance'
        verbose_name_plural = 'Finance'

class Agent(User):
    pass

    class Meta:
        verbose_name = 'Agents'
        verbose_name_plural = 'Agents'
        
class Manager(User):
    pass

    class Meta:
        verbose_name = 'Manager'
        verbose_name_plural = 'Managers'
        
class Veterinary(User):
    pass

    class Meta:
        verbose_name = 'Veterinary'
        verbose_name_plural = 'Veterinaries'
        

        

# class UserProfileManager(BaseUserManager):
#     """Helps Django work with our custom user model."""

#     def create_user(self, email, username, password=None):
#         """Creates a user profile object."""

#         if not email:
#             raise ValueError('User must have an email address.')

#         email = self.normalize_email(email)
#         user = self.model(email=email, username=username)

#         user.user_id = -1
#         user.set_password(password)
#         user.save(using=self._db)

#         return user
