from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import MilkCollection
from django.db.models import Sum
from django.utils.dateformat import DateFormat
from collections import defaultdict

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
