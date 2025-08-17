from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
     path('payments/', views.payment_statements, name='payment_statements'),
     path('payments/pdf/', views.export_payment_statements_pdf, name='export_payment_statements_pdf'),
     
     # finance manager
    path('finance-dashboard', views.finance_dashboard, name='finance_dashboard'),
    path('milk-prices/', views.milk_price_list, name='milk_price_list'),
    path('milk-prices/add/', views.add_milk_price, name='add_milk_price'),
    path('milk-prices/<int:pk>/edit/', views.edit_milk_price, name='edit_milk_price'),
    path('milk-prices/<int:pk>/delete/', views.delete_milk_price, name='delete_milk_price'),
    path('payments-add_milk_price/', views.payment_list, name='payment_list'),
    path('payment-detail/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('pending-payments/', views.pending_payments, name='pending_payments'),
    path('mark-paid/<int:pk>/mark-paid/', views.mark_payment_paid, name='mark_payment_paid'),
    path('finance-reports/', views.payments_reports, name='payments_reports'),
   path("export-payments-pdf/", views.export_payments_pdf, name="export_payments_pdf"),

    
]
