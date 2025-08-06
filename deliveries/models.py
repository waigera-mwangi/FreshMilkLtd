from django.db import models

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal

# Timestamp Base
class TimeStamp(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Pickup Locations
class PickupLocation(models.Model):
    name = models.CharField(max_length=100)
    town = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.town})"


# Milk Collection
class MilkCollection(TimeStamp):
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'FR'},  # Only Farmers
        related_name='milk_collections'
    )
    field_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'FA'},  # Only Field Agents
        related_name='collected_milk'
    )
    pickup_location = models.ForeignKey(
        PickupLocation,
        on_delete=models.CASCADE,
        related_name='milk_collections'
    )
    quantity_liters = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.10'))]
    )
    collection_date = models.DateField()
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.farmer.get_full_name()} - {self.quantity_liters} L"

    class Meta:
        ordering = ['-collection_date']


# Field Supervision Log
class FieldSupervision(TimeStamp):
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'FD'},  # Field Manager
        related_name='supervisions'
    )
    field_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'FA'},
        related_name='supervised_by'
    )
    notes = models.TextField()
    supervision_date = models.DateField()

    def __str__(self):
        return f"Supervision by {self.manager.get_full_name()} on {self.supervision_date}"
