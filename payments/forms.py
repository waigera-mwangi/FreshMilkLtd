from django import forms
from .models import MilkPrice

class MilkPriceForm(forms.ModelForm):
    class Meta:
        model = MilkPrice
        fields = ['price_per_liter', 'effective_date', 'is_active']
        widgets = {
            'effective_date': forms.DateInput(attrs={'type': 'date'}),
        }