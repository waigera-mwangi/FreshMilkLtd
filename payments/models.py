# payments/models.py

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from django.core.validators import MinValueValidator

# Timestamp base
class TimeStamp(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Milk Price (can change over time)
class MilkPrice(TimeStamp):
    price_per_liter = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.10'))],
        help_text="Current price per liter in currency units."
    )
    effective_date = models.DateField(help_text="Date this price becomes effective")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-effective_date']

    def __str__(self):
        return f"{self.price_per_liter} per L (Effective {self.effective_date})"


# Farmer Payment
class Payment(TimeStamp):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PAID = 'PAID', _('Paid')

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'FR'},
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(help_text="Start of payment period")
    end_date = models.DateField(help_text="End of payment period")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Payment to {self.farmer.get_full_name()} - {self.amount} ({self.status})"

    class Meta:
        ordering = ['-created']
