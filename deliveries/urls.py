from django.urls import path
from . import views

app_name = 'deliveries'

urlpatterns = [
    path('dashboard/', views.view_deliveries, name='view-deliveries'),
    path('milk-history/', views.milk_history, name='milk_history'),
    path('milk-history/export/pdf/', views.export_milk_history_pdf, name='export_milk_history_pdf'),
    
    # field agent
    path('filed-agent-dashboard/', views.dashboard, name='field_agent_dashboard'),
    path('record-collection/', views.record_collection, name='record_collection'),
    path('get-farmer-name/', views.get_farmer_name, name='get_farmer_name'),
    # path('milk-collection/', views.milk_collection_list, name='milk_collection_list'),
    # path('milk-collection/add/', views.milk_collection_create, name='milk_collection_create'),
    # path('farmers/', views.farmers_list, name='farmers_list'),
    # path('farmers/<int:pk>/', views.farmer_detail, name='farmer_detail'),
    
    ]
