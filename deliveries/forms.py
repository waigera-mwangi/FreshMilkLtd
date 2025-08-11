from django import forms
from .models import MilkCollection
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
