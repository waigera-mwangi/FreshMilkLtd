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
        CUSTOMER = 'CM', _('CUSTOMER')
        DRIVER = 'DR', _('DRIVER')
        INVENTORY_MANAGER = 'IM', _('INVENTORY MANAGER')
        SERVICE_PROVIDER = 'SP', _('SERVICE PROVIDER')
        SUPPLIER = 'SR', _('SUPPLIER')
        INSTALLER = 'IS', _('INSTALLER')
        FINANCE_MANAGER = 'FM', _('FINANCE MANAGER')
        ADMIN = 'AD', _('ADMIN')
        
    user_type = models.CharField(
        max_length=2,
        choices = UserTypes.choices,
        default=UserTypes.CUSTOMER,
    )
    first_name = models.CharField( max_length=250)
    last_name = models.CharField( max_length=250)
    phone_number = CustomPhoneNumberField(unique=True, null=True)
    county = models.CharField(max_length=20)
    town = models.CharField(max_length=20)
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
    county = models.CharField(max_length=20)
    town = models.CharField(max_length=20)
    is_active = models.BooleanField(_('Active'), default=True, help_text=_('Activated, users profile is published'))
    updated = models.DateField(_('Updated'), auto_now=True)
    created = models.DateField(_('Created'), auto_now_add=True)
    gender = models.CharField(
        max_length=2,
        choices=Gender.choices,
        default=Gender.MALE,
    )
    
# customer
class CustomerProfile(Profile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')

    class Meta:
        verbose_name = 'Customer Profile'
        verbose_name_plural = 'Customer Profile'
        
# finance manager
class FinanceProfile(Profile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='finance_profile')

    class Meta:
        verbose_name = 'Finance Profile'
        verbose_name_plural = 'Finance Profile'
# installer
class InstallerProfile(Profile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='installer_profile')

    class Meta:
        verbose_name = 'Installer Profile'
        verbose_name_plural = 'Installer Profile'

# driver
class DriverProfile(Profile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')

    class Meta:
        verbose_name = 'Driver Profile'
        verbose_name_plural = 'Driver Profile'
#  service
class ServiceProfile(Profile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='service_provider_profile')

    class Meta:
        verbose_name = 'Service Profile'
        verbose_name_plural = 'Service Profile'
        
class SupplierProfile(Profile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supplier_profile')

    class Meta:
        verbose_name = 'Supplier Profile'
        verbose_name_plural = 'Supplier Profile'

class Customer(User):
    pass

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        
class Finance(User):
    pass

    class Meta:
        verbose_name = 'Finance'
        verbose_name_plural = 'Finance'

class Supply(User):
    pass

    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        
class Service(User):
    pass

    class Meta:
        verbose_name = 'Service_Manager'
        verbose_name_plural = 'Service_Managers'
        
class Inventory(User):
    pass

    class Meta:
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventory'
        
class Driver(User):
    pass

    class Meta:
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'
        

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
