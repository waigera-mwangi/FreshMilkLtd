from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
     path('payments/', views.payment_statements, name='payment_statements'),
     path('payments/pdf/', views.export_payment_statements_pdf, name='export_payment_statements_pdf'),
     
     # finance manager
    path('finance-dashboard', views.finance_dashboard, name='finance_dashboard'),
    path('milk-prices/', views.milk_price_list, name='milk_price_list'),
    path('milk-prices/add/', views.milk_price_create, name='milk_price_create'),
    path('payments-list/', views.payment_list, name='payment_list'),
    path('payment-detail/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('mark-paid/<int:pk>/mark-paid/', views.mark_payment_paid, name='mark_payment_paid'),
    path('finance-reports/', views.reports, name='reports'),
]
