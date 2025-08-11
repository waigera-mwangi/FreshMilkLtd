# forms.py
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
        if commit:
            instance.save()
        return instance




# views.py
from django.http import JsonResponse
from django.contrib.auth import get_user_model
User = get_user_model()

def get_farmer_name(request):
    farmer_id = request.GET.get('farmer_id')
    try:
        farmer = User.objects.get(farmer_id=farmer_id, user_type=User.UserTypes.FARMER)
        return JsonResponse({'name': farmer.get_full_name()}, status=200)
    except User.DoesNotExist:
        return JsonResponse({'name': ''}, status=404)
