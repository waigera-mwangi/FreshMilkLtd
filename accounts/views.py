from django.contrib.auth import logout, authenticate, login, update_session_auth_hash
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views import View
from django.urls import reverse_lazy
from accounts.decorators import required_access
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import CreateView
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import User
from accounts.models import *
from accounts.forms import *


# Create your views here.
class LogoutView(View):

    def get(self, *args, **kwargs):
        logout(self.request)
        messages.info(self.request, "You've logged out successfully.")
        return redirect('/')
    
    
class UserCreateView(SuccessMessageMixin, CreateView):
    template_name = "accounts/farmer-register.html"
    form_class = FarmerSignUpForm
    model = User
    success_message = "You've registered successfully"
    success_url = reverse_lazy('accounts:login')



def loginView(request):
    loginform = LoginForm(request.POST or None)
    msg = ''

    if request.method == 'POST':
        if loginform.is_valid():
            username = loginform.cleaned_data.get('username').lower()
            password = loginform.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    if user.user_type == "FR":
                        login(request, user)
                        return redirect('accounts:farmer')
                    
                    elif user.user_type == "FM":
                        login(request, user)
                        return redirect('accounts:finance_manager')
                    
                    elif user.user_type == "FA":
                        login(request, user)
                        return redirect('accounts:field_agent')
                    
                    elif user.user_type == "FD":
                        login(request, user)
                        return redirect('accounts:field_manager')
                    
                    elif user.user_type == "VO":
                        login(request, user)
                        return redirect('accounts:veterinary')
                    
                else:
                    messages.warning(request, 'Waiting for admin approval')
            else:
                messages.warning(request, 'Check for incorrect details, else wait for approval')
        else:
            messages.warning(request, 'Invalid form submission')
# results

    return render(request, 'accounts/user-login.html', {'form': loginform, 'msg': msg})



# farmer
@required_access(login_url=reverse_lazy('accounts:login'), user_type="FR")
def farmer(request):

    return redirect('deliveries:view-deliveries')

# finance_manager
@required_access(login_url=reverse_lazy('accounts:login'), user_type="FM")
def finance_manager(request):
    return redirect('payments:finance_dashboard')

# field_agent
@required_access(login_url=reverse_lazy('accounts:login'), user_type="FA")
def field_agent(request):
      return render(request, 'field_agent/pages/index.html')

# field manager
@required_access(login_url=reverse_lazy('accounts:login'), user_type="FD")
def field_manager(request):
        return render(request, 'field_manager/pages/index.html')

@required_access(login_url=reverse_lazy('accounts:login'), user_type="VO")
def veterinary(request):
       return redirect('veterinary:vet_dashboard')


#Change password
def password_change(request):
    form = PasswordChangeForm(request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important
            messages.success(request, 'Your password was successfully updated!')
        else:
            messages.info(request, 'Please correct the errors below.')
    return render(request, 'accounts/change-password.html', {'form': form})
