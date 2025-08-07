from django.urls import path
from . import views

app_name = 'veterinary'

urlpatterns = [
    path('vet-services/', views.farmer_vet_requests_list, name='farmer_vet_requests'),
    path('vet-services/request/', views.request_vet_service, name='request_vet_service'),
    path('about/', views.about_us, name='about_us'),
]