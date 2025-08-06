from django.contrib import admin, messages
from django.http import HttpResponse
from .models import VetServiceType, VetServiceRequest, VetTreatmentRecord
from django.utils.translation import ngettext
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# -------------------------
# PDF Export Utility
# -------------------------
def export_requests_to_pdf(queryset):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="vet_service_requests.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    p.setFont("Helvetica", 12)
    y = 750
    p.drawString(200, 800, "Veterinary Service Requests Report")

    for req in queryset:
        line = f"Farmer: {req.farmer.get_full_name()} | Service: {req.service_type.name} | Status: {req.status} | Date: {req.request_date.date()}"
        p.drawString(50, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 750

    p.showPage()
    p.save()
    return response


# -------------------------
# Vet Service Type Admin
# -------------------------
@admin.register(VetServiceType)
class VetServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('name',)


# -------------------------
# Vet Service Request Admin
# -------------------------
@admin.register(VetServiceRequest)
class VetServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('farmer_name', 'service_type', 'status', 'appointment_date', 'vet_officer_name')
    list_filter = ('status', 'service_type', 'request_date', 'appointment_date')
    search_fields = ('farmer__first_name', 'farmer__last_name', 'vet_officer__first_name')
    date_hierarchy = 'request_date'
    ordering = ('-request_date',)
    actions = ['approve_requests', 'mark_as_completed', 'export_as_pdf']

    def farmer_name(self, obj):
        return obj.farmer.get_full_name()
    farmer_name.short_description = 'Farmer'

    def vet_officer_name(self, obj):
        return obj.vet_officer.get_full_name() if obj.vet_officer else 'Not Assigned'
    vet_officer_name.short_description = 'Vet Officer'

    # Action: Approve Requests
    def approve_requests(self, request, queryset):
        updated = queryset.update(status=VetServiceRequest.RequestStatus.APPROVED)
        self.message_user(request, ngettext(
            '%d request approved.',
            '%d requests approved.',
            updated,
        ) % updated, messages.SUCCESS)
    approve_requests.short_description = "Approve selected requests"

    # Action: Mark as Completed
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status=VetServiceRequest.RequestStatus.COMPLETED)
        self.message_user(request, ngettext(
            '%d request marked as completed.',
            '%d requests marked as completed.',
            updated,
        ) % updated, messages.SUCCESS)
    mark_as_completed.short_description = "Mark selected as completed"

    # Action: Export as PDF
    def export_as_pdf(self, request, queryset):
        return export_requests_to_pdf(queryset)
    export_as_pdf.short_description = "Export selected requests to PDF"


# -------------------------
# Vet Treatment Record Admin
# -------------------------
@admin.register(VetTreatmentRecord)
class VetTreatmentRecordAdmin(admin.ModelAdmin):
    list_display = ('request', 'completed_on')
    search_fields = ('request__farmer__first_name', 'request__farmer__last_name')
    date_hierarchy = 'completed_on'
    ordering = ('-completed_on',)
