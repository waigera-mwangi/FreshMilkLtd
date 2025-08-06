from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from deliveries.models import MilkCollection

# -------------------------
# Milk Price Model
# -------------------------
class MilkPrice(models.Model):
    price_per_liter = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.10'))],
        help_text="Current price per liter of milk"
    )
    effective_date = models.DateField(help_text="Date this price becomes active")
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Deactivate previous active prices when this becomes active
        if self.is_active:
            MilkPrice.objects.exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.price_per_liter} KES effective {self.effective_date}"

    class Meta:
        ordering = ['-effective_date']


# -------------------------
# Farmer Payments
# -------------------------

class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PAID = 'PAID', _('Paid')
        FAILED = 'FAILED', _('Failed')
    
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'FR'},  # Only Farmers
        related_name='payments'
    )
    milk_collections = models.ManyToManyField(MilkCollection, related_name='payments', blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    generated_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    reference = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Payment to {self.farmer.get_full_name()} - {self.amount} KES"

    class Meta:
        ordering = ['-generated_on']