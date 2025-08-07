from django import forms
from django.contrib.auth.forms import UserCreationForm, ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


# -------------------
# Admin Change Form
# -------------------
class UserAdminChangeForm(forms.ModelForm):
    """
    Form for updating users in Django Admin.
    Replaces the password field with the hashed display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'phone_number',
                  'town', 'location', 'user_type', 'is_active']

    def clean_password(self):
        # Return the initial password value regardless of user input
        return self.initial["password"]
    
    def clean_user_type(self):
        user_type = self.cleaned_data.get('user_type')
        if not user_type:
            raise forms.ValidationError("User type is required.")
        return user_type



# -------------------
# Admin Add Form (for superusers)
# -------------------
class RegistrationForm(UserCreationForm):
    """
    Form for creating new users in Django Admin.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'phone_number', 'user_type', 'town', 'location']

    def clean_username(self):
        return self.cleaned_data['username'].upper()


# -------------------
# Custom Login Form
# -------------------
class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"})
    )


# -------------------
# Public Sign-Up Form (for customers/farmers)
# -------------------
class FarmerSignUpForm(UserCreationForm):
    """
    Form for registering normal customers/farmers from the frontend.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = "FR"  # Default to Farmer
        if commit:
            user.save()
        return user


# -------------------
# Custom Authentication Form
# -------------------
class FarmerAuthenticationForm(AuthenticationForm):
    def clean(self):
        super().clean()
        if self.user_cache is not None:
            if self.user_cache.is_superuser:
                logout(self.request)
                raise forms.ValidationError("Admins must log in through the admin panel.", code='invalid_login')