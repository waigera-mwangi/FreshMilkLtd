from django.urls import path
from . import views

app_name = 'veterinary'

urlpatterns = [
    path('vet-services/', views.farmer_vet_requests_list, name='farmer_vet_requests'),
    path('vet-services/request/', views.request_vet_service, name='request_vet_service'),
    path('about/', views.about_us, name='about_us'),
    
    # veterinary
    path('', views.veterinary, name='vet_home'),
    path('vet-dashboard/', views.vet_dashboard, name='vet_dashboard'),
    path('assigned/', views.assigned_requests, name='assigned_requests'),
    path('request/<int:pk>/update/', views.update_request, name='update_request'),
    path('request/<int:pk>/treatment/', views.add_treatment_record, name='add_treatment_record'),
    path('treatment-records/', views.treatment_record_list, name='treatment_record_list'),
    path('vet-service-requests/', views.vet_service_requests, name='vet_service_requests'),

]