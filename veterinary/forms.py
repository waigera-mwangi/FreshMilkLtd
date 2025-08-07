from django import forms
from .models import VetServiceRequest

class VetServiceRequestForm(forms.ModelForm):
    class Meta:
        model = VetServiceRequest
        fields = ['service_type', 'description', 'appointment_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the issue...'}),
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
        }
