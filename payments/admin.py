from django.contrib import admin, messages
from django.utils.translation import ngettext
from datetime import date, timedelta
from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate
from .models import *
from .utils import calculate_and_create_payment
from accounts.models import User


@admin.register(MilkPrice)
class MilkPriceAdmin(admin.ModelAdmin):
    list_display = ('price_per_liter', 'effective_date', 'is_active')
    list_filter = ('is_active', 'effective_date')
    ordering = ('-effective_date',)

    def save_model(self, request, obj, form, change):
        # Ensure only one active price
        if obj.is_active:
            MilkPrice.objects.update(is_active=False)
            obj.is_active = True
        super().save_model(request, obj, form, change)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'amount', 'start_date', 'end_date', 'status', 'reference')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('farmer__first_name', 'farmer__last_name', 'reference')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)
    actions = [
        'generate_weekly_payments',
        'generate_monthly_payments',
        'mark_as_paid',
        'mark_as_failed',
        'export_as_pdf',
    ]

    def generate_weekly_payments(self, request, queryset):
        today = date.today()
        start_date = today - timedelta(days=7)
        end_date = today

        farmers = User.objects.filter(user_type='FR')
        created_count = 0

        for farmer in farmers:
            payment = calculate_and_create_payment(farmer, start_date, end_date)
            if payment:
                created_count += 1

        self.message_user(request, ngettext(
            '%d weekly payment generated.',
            '%d weekly payments generated.',
            created_count,
        ) % created_count, messages.SUCCESS)
    generate_weekly_payments.short_description = "Generate Weekly Payments"

    def generate_monthly_payments(self, request, queryset):
        today = date.today()
        start_date = today.replace(day=1) - timedelta(days=30)
        end_date = today

        farmers = User.objects.filter(user_type='FR')
        created_count = 0

        for farmer in farmers:
            payment = calculate_and_create_payment(farmer, start_date, end_date)
            if payment:
                created_count += 1

        self.message_user(request, ngettext(
            '%d monthly payment generated.',
            '%d monthly payments generated.',
            created_count,
        ) % created_count, messages.SUCCESS)
    generate_monthly_payments.short_description = "Generate Monthly Payments"

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status=Payment.PaymentStatus.PAID)
        self.message_user(request, f"{updated} payments marked as PAID", messages.SUCCESS)
    mark_as_paid.short_description = "Mark selected as Paid"

    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status=Payment.PaymentStatus.FAILED)
        self.message_user(request, f"{updated} payments marked as FAILED", messages.ERROR)
    mark_as_failed.short_description = "Mark selected as Failed"
    
    
# export to pdf
    
    def export_as_pdf(self, request, queryset):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Define table data
        data = [['Farmer', 'Amount (KES)', 'Start Date', 'End Date', 'Status']]  # table headers

        for payment in queryset:
            data.append([
                payment.farmer.get_full_name(),
                f"{payment.amount:.2f}",
                str(payment.start_date),
                str(payment.end_date),
                payment.status
            ])

        # Create table and apply styles
        table = Table(data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))

        elements.append(table)
        doc.build(elements)

        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf', headers={
            'Content-Disposition': 'attachment; filename="payments_report.pdf"'
        })

    export_as_pdf.short_description = "Export Selected Payments to PDF"
