from django.contrib import admin, messages
from .models import MilkPrice, Payment
from .utils import calculate_and_create_payment
from datetime import date, timedelta
from django.utils.translation import ngettext
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO


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
    list_display = ('farmer_name', 'amount', 'start_date', 'end_date', 'status', 'reference')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('farmer__first_name', 'farmer__last_name', 'reference')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)
    actions = ['generate_weekly_payments', 'generate_monthly_payments', 'export_as_pdf']

    def farmer_name(self, obj):
        return obj.farmer.get_full_name()
    farmer_name.short_description = 'Farmer'

    # Weekly Payment Generation
    def generate_weekly_payments(self, request, queryset):
        today = date.today()
        start_date = today - timedelta(days=7)
        end_date = today
        farmers = queryset.values_list('farmer', flat=True).distinct()
        created_count = 0

        for farmer_id in farmers:
            from accounts.models import User
            farmer = User.objects.get(id=farmer_id)
            payment = calculate_and_create_payment(farmer, start_date, end_date)
            if payment:
                created_count += 1

        self.message_user(request, ngettext(
            '%d weekly payment generated.',
            '%d weekly payments generated.',
            created_count,
        ) % created_count, messages.SUCCESS)

    generate_weekly_payments.short_description = "Generate Weekly Payments"

    # Monthly Payment Generation
    def generate_monthly_payments(self, request, queryset):
        today = date.today()
        start_date = today.replace(day=1) - timedelta(days=30)
        end_date = today
        farmers = queryset.values_list('farmer', flat=True).distinct()
        created_count = 0

        for farmer_id in farmers:
            from accounts.models import User
            farmer = User.objects.get(id=farmer_id)
            payment = calculate_and_create_payment(farmer, start_date, end_date)
            if payment:
                created_count += 1

        self.message_user(request, ngettext(
            '%d monthly payment generated.',
            '%d monthly payments generated.',
            created_count,
        ) % created_count, messages.SUCCESS)

    generate_monthly_payments.short_description = "Generate Monthly Payments"

    # Export as PDF
    def export_as_pdf(self, request, queryset):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        y = 750
        p.setFont("Helvetica", 12)
        p.drawString(200, 800, "Payment Report")

        for payment in queryset:
            p.drawString(50, y, f"Farmer: {payment.farmer.get_full_name()}, Amount: {payment.amount}, "
                                f"Period: {payment.start_date} - {payment.end_date}, Status: {payment.status}")
            y -= 20
            if y < 50:
                p.showPage()
                y = 750

        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="payments_report.pdf"'
        return response

    export_as_pdf.short_description = "Export Selected Payments to PDF"
