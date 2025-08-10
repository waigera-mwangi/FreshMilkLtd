from django import forms
from .models import MilkCollection
from django.contrib.auth import get_user_model

class MilkCollectionForm(forms.ModelForm):
    farmer_id = forms.CharField(label="Farmer ID")
    farmer_name = forms.CharField(label="Farmer Name", required=False, disabled=True)

    class Meta:
        model = MilkCollection
        fields = ['farmer_id', 'farmer_name', 'quantity_liters', 'pickup_location']

    def clean_farmer_id(self):
        User = get_user_model()
        farmer_id = self.cleaned_data['farmer_id']
        try:
            farmer = User.objects.get(username=farmer_id, user_type='FR')
        except User.DoesNotExist:
            raise forms.ValidationError("Farmer with this ID does not exist.")
        self.cleaned_data['farmer'] = farmer
        return farmer_id

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.farmer = self.cleaned_data['farmer']
        if commit:
            instance.save()
        return instance
