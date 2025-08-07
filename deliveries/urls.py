from django.urls import path
from . import views

app_name = 'deliveries'

urlpatterns = [
    path('dashboard/', views.view_deliveries, name='view-deliveries'),
     path('milk-history/', views.milk_history, name='milk_history'),
     path('milk-history/export/pdf/', views.export_milk_history_pdf, name='export_milk_history_pdf'),
    
    ]
