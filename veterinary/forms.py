from django import forms
from .models import *

class VetServiceRequestForm(forms.ModelForm):
    class Meta:
        model = VetServiceRequest
        fields = ['service_type', 'description', 'appointment_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the issue...'}),
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
        }



class VetServiceRequestUpdateForm(forms.ModelForm):
    class Meta:
        model = VetServiceRequest
        fields = ['status', 'appointment_date', 'cost']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'cost': forms.NumberInput(attrs={'step': '0.01'}),
        }

class VetTreatmentRecordForm(forms.ModelForm):
    class Meta:
        model = VetTreatmentRecord
        fields = ['treatment_details', 'follow_up_date']  # ❌ remove 'notes'
