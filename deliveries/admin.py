from django.contrib import admin
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from .models import PickupLocation, MilkCollection, FieldSupervision


# -----------------------
# PDF Export Action
# -----------------------
def export_milk_collection_pdf(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="milk_collections.pdf"'

    # Create the PDF
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Milk Collections Report")

    # Table Header
    p.setFont("Helvetica-Bold", 10)
    y = height - 100
    p.drawString(30, y, "Farmer")
    p.drawString(150, y, "Field Agent")
    p.drawString(270, y, "Pickup Location")
    p.drawString(400, y, "Qty (L)")
    p.drawString(470, y, "Date")

    y -= 20

    # Add Data
    p.setFont("Helvetica", 9)
    for obj in queryset:
        if y < 50:  # Start new page if space runs out
            p.showPage()
            y = height - 50

        farmer = obj.farmer.get_full_name()
        agent = obj.field_agent.get_full_name() if obj.field_agent else "N/A"
        location = obj.pickup_location.name
        qty = str(obj.quantity_liters)
        date = obj.collection_date.strftime("%Y-%m-%d")

        p.drawString(30, y, farmer[:15])  # Limit text length
        p.drawString(150, y, agent[:15])
        p.drawString(270, y, location[:15])
        p.drawString(400, y, qty)
        p.drawString(470, y, date)

        y -= 18

    p.showPage()
    p.save()
    return response


export_milk_collection_pdf.short_description = "Export selected Milk Collections to PDF"


# -----------------------
# PICKUP LOCATION ADMIN
# -----------------------
@admin.register(PickupLocation)
class PickupLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'town', 'is_active')
    search_fields = ('name', 'town')
    list_filter = ('is_active',)
    ordering = ('name',)


# -----------------------
# MILK COLLECTION ADMIN
# -----------------------
@admin.register(MilkCollection)
class MilkCollectionAdmin(admin.ModelAdmin):
    list_display = ('farmer_name', 'field_agent_name', 'pickup_location', 'quantity_liters', 'collection_date')
    list_filter = ('pickup_location', 'collection_date', 'field_agent')
    search_fields = ('farmer__first_name', 'farmer__last_name', 'field_agent__first_name', 'pickup_location__name')
    date_hierarchy = 'collection_date'
    ordering = ('-collection_date',)
    actions = [export_milk_collection_pdf]  # ✅ Added PDF Export

    def farmer_name(self, obj):
        return obj.farmer.get_full_name()
    farmer_name.short_description = 'Farmer'

    def field_agent_name(self, obj):
        return obj.field_agent.get_full_name() if obj.field_agent else 'N/A'
    field_agent_name.short_description = 'Field Agent'


# -----------------------
# FIELD SUPERVISION ADMIN
# -----------------------
@admin.register(FieldSupervision)
class FieldSupervisionAdmin(admin.ModelAdmin):
    list_display = ('manager_name', 'field_agent_name', 'supervision_date', 'notes')
    list_filter = ('supervision_date', 'manager', 'field_agent')
    search_fields = ('manager__first_name', 'manager__last_name', 'field_agent__first_name')
    date_hierarchy = 'supervision_date'
    ordering = ('-supervision_date',)

    def manager_name(self, obj):
        return obj.manager.get_full_name()
    manager_name.short_description = 'Manager'

    def field_agent_name(self, obj):
        return obj.field_agent.get_full_name()
    field_agent_name.short_description = 'Field Agent'
