from django.urls import path
from . import views

app_name = 'deliveries'

urlpatterns = [
    path('dashboard/', views.view_deliveries, name='view-deliveries'),
    
    ]
