from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
     path('payments/', views.payment_statements, name='payment_statements'),
     path('payments/pdf/', views.export_payment_statements_pdf, name='export_payment_statements_pdf'),

     
]