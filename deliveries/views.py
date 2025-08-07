from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import MilkCollection
from django.db.models import Sum
from django.utils.dateformat import DateFormat
from collections import defaultdict
from decimal import Decimal
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa


@login_required
def view_deliveries(request):
    farmer = request.user
    deliveries = MilkCollection.objects.filter(farmer=farmer).order_by('collection_date')

    # Existing data
    total_litres = deliveries.aggregate(Sum('quantity_liters'))['quantity_liters__sum'] or 0
    unpaid_amount = sum([
        d.quantity_liters * d.price_per_liter
        for d in deliveries if not d.is_paid
    ])

    # New: Prepare chart data (quantity per day)
    
    stats = defaultdict(float)
    for d in deliveries:
        date_label = DateFormat(d.collection_date).format('M d')  # e.g. 'Aug 07'
        stats[date_label] += float(d.quantity_liters)


    chart_labels = list(stats.keys())
    chart_data = list(stats.values())

    context = {
        'deliveries': deliveries,
        'total_litres': total_litres,
        'unpaid_amount': unpaid_amount,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }

    return render(request, 'farmer/pages/farmer_dashboard.html', context)

#  farmer view milk history

@login_required
def milk_history(request):
    farmer = request.user
    deliveries = MilkCollection.objects.filter(farmer=farmer).order_by('-collection_date')
    
    grand_total = Decimal(0)
    total_quantity = Decimal(0)
    grand_total = Decimal(0)
    paid_total = Decimal(0)
    unpaid_total = Decimal(0)
    paid_quantity = Decimal(0)
    unpaid_quantity = Decimal(0)
    
    
    for delivery in deliveries:
        delivery.total_amount = Decimal(str(delivery.quantity_liters)) * Decimal(str(delivery.price_per_liter))
        grand_total += delivery.total_amount
        total_quantity += Decimal(str(delivery.quantity_liters))

        if delivery.is_paid:
            paid_total += delivery.total_amount
            paid_quantity += Decimal(str(delivery.quantity_liters))
        else:
            unpaid_total += delivery.total_amount
            unpaid_quantity += Decimal(str(delivery.quantity_liters))

    context = {
        'deliveries': deliveries,
        'grand_total': grand_total,
        'total_quantity': total_quantity,
        'paid_total': paid_total,
        'unpaid_total': unpaid_total,
        'paid_quantity': paid_quantity,
        'unpaid_quantity': unpaid_quantity,
    }
    return render(request, 'farmer/pages/milk_history.html', context)


# farmer export to pdf
@login_required
def export_milk_history_pdf(request):
    farmer = request.user
    deliveries = MilkCollection.objects.filter(farmer=farmer).order_by('-collection_date')

    # Totals
    from decimal import Decimal
    grand_total = Decimal(0)
    total_quantity = Decimal(0)

    for d in deliveries:
        d.total_amount = Decimal(str(d.quantity_liters)) * Decimal(str(d.price_per_liter))
        grand_total += d.total_amount
        total_quantity += Decimal(str(d.quantity_liters))

    template_path = 'farmer/pages/milk_history_pdf.html'
    context = {
        'deliveries': deliveries,
        'grand_total': grand_total,
        'total_quantity': total_quantity,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="milk_history.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation failed')
    return response
