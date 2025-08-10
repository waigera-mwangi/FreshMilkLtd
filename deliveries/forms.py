# forms.py
from django import forms
from .models import MilkCollection

class MilkCollectionForm(forms.ModelForm):
    farmer_id = forms.IntegerField(label="Farmer ID")
    farmer_name = forms.CharField(label="Farmer Name", required=False, disabled=True)

    class Meta:
        model = MilkCollection
        fields = ['farmer_id', 'farmer_name', 'quantity_liters', 'pickup_location', 'collection_date']

    def clean_farmer_id(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        farmer_id = self.cleaned_data['farmer_id']
        try:
            farmer = User.objects.get(id=farmer_id, user_type='FR')
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
