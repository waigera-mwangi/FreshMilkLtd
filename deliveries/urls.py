from django.urls import path
from . import views

app_name = 'deliveries'

urlpatterns = [
    path('dashboard/', views.view_deliveries, name='view-deliveries'),
    path('milk-history/', views.milk_history, name='milk_history'),
    path('milk-history/export/pdf/', views.export_milk_history_pdf, name='export_milk_history_pdf'),
    
    # field agent
    path('filed-agent-dashboard/', views.dashboard, name='field_agent_dashboard'),
    path('get-farmer-name/', views.get_farmer_name, name='get_farmer_name'),
    path('record-collection/', views.record_collection, name='record_collection'),
    # path('milk-collection/', views.milk_collection_list, name='milk_collection_list'),
    # path('milk-collection/add/', views.milk_collection_create, name='milk_collection_create'),
    # path('farmers/', views.farmers_list, name='farmers_list'),
    # path('farmers/<int:pk>/', views.farmer_detail, name='farmer_detail'),
    
    # field manager
    path("manager-dashboard/", views.manager_dashboard, name="manager_dashboard"),
    path("pickup-locations/", views.pickup_locations, name="pickup_locations"),
    path("pickup-locations/add/", views.add_pickup_location, name="add_pickup_location"),
    path("pickup-locations/<int:pk>/edit/", views.edit_pickup_location, name="edit_pickup_location"),
    path("pickup-locations/<int:pk>/delete/", views.delete_pickup_location, name="delete_pickup_location"),
    path("milk-collections/", views.milk_collections_report, name="milk_collections_report"),
    path("supervisions/", views.supervisions, name="supervisions"),
    
    ]
