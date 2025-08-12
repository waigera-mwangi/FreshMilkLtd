from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# -------------------------
# Veterinary Service Types
# -------------------------
class VetServiceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Veterinary Service Type"
        verbose_name_plural = "Veterinary Service Types"


# -------------------------
# Veterinary Service Requests
# -------------------------
class VetServiceRequest(models.Model):
    class RequestStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'FR'},
        related_name='vet_requests'
    )
    vet_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'VO'},
        related_name='assigned_requests'
    )
    service_type = models.ForeignKey(VetServiceType, on_delete=models.CASCADE)
    description = models.TextField()
    request_date = models.DateTimeField(auto_now_add=True)
    appointment_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING
    )
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.service_type.name} for {self.farmer.get_full_name()}"

    class Meta:
        ordering = ['-request_date']


# -------------------------
# Treatment Records (Optional)
# -------------------------
class VetTreatmentRecord(models.Model):
    request = models.OneToOneField(
        VetServiceRequest,
        on_delete=models.CASCADE,
        related_name='treatment_record'
    )
    treatment_details = models.TextField()
    completed_on = models.DateTimeField(auto_now_add=True)
    follow_up_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Treatment for {self.vet_request}"
