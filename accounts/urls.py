from django.urls import path, reverse_lazy
from accounts import views
from accounts.views import *
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from accounts.decorators import required_access
# from store.views import *

app_name = "accounts"

urlpatterns = [
    path('register/', UserCreateView.as_view(), name="register"),
    path('logout/', LogoutView.as_view(), name="logout"),
    
    path('', views.loginView, name='login'),
    path('farmer/', views.farmer, name='farmer'),
    path('finance_manager/', views.finance_manager, name='finance_manager'),
    path('field_agent/', views.field_agent, name='field_agent'),
    path('field_manager/', views.field_manager, name='field_manager'),
    path('veterinary/', views.veterinary, name='veterinary'),
    
 
       # profile
    # path('farmer-profile', customer_profile, name='farmer-profile'),
    # path('finance-profile', finance_profile, name='finance-profile'),
    # path('brander-profile', brander_profile, name='brander-profile'),
    # path('dispatch-profile', dispatch_profile, name='dispatch-profile'),
    # path('driver-profile', driver_profile, name='driver-profile'),
    # path('inventory-profile', inventory_profile, name='inventory-profile'),
    # path('supplier-profile', supplier_profile, name='supplier-profile'),
    
    
]