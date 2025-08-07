from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('faq/', views.faq_list, name='faq'),
    path('feedback/', views.submit_feedback, name='feedback'),
    path('thank-you/', views.thank_you, name='thank_you'),
]
