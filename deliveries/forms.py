from django import forms
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()

class MilkCollectionForm(forms.ModelForm):
    farmer_id = forms.CharField(label="Farmer ID")
    farmer_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = MilkCollection
        fields = ['farmer_id', 'farmer_name', 'pickup_location', 'quantity_liters']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # store request for access to logged-in user
        super().__init__(*args, **kwargs)

    def clean_farmer_id(self):
        farmer_id = self.cleaned_data['farmer_id']
        try:
            farmer = User.objects.get(farmer_id=farmer_id, user_type=User.UserTypes.FARMER)
        except User.DoesNotExist:
            raise forms.ValidationError("Farmer with this ID does not exist.")
        self.cleaned_data['farmer'] = farmer
        self.cleaned_data['farmer_name'] = farmer.get_full_name()
        return farmer_id

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.farmer = self.cleaned_data['farmer']

        # automatically set the field agent
        if self.request and self.request.user.is_authenticated:
            instance.field_agent = self.request.user

        if commit:
            instance.save()
        return instance






class PickupLocationForm(forms.ModelForm):
    class Meta:
        model = PickupLocation
        fields = ["name", "town", "description", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter pickup location name"}),
            "town": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter town"}),
            "description": forms.Textarea(attrs={"class": "form-control", "placeholder": "Optional description", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "name": "Location Name",
            "town": "Town",
            "description": "Description",
            "is_active": "Active",
        }


class FieldSupervisionForm(forms.ModelForm):
    class Meta:
        model = FieldSupervision
        fields = ["field_agent", "supervision_date", "notes"]
        widgets = {
            "supervision_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }
