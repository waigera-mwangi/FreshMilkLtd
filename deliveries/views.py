# deliveries/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import MilkCollection

@login_required
def view_deliveries(request):
    farmer = request.user
    deliveries = MilkCollection.objects.filter(farmer=farmer).order_by('-collection_date')

    total_litres = deliveries.aggregate(models.Sum('quantity_liters'))['quantity_liters__sum'] or 0
    unpaid_amount = sum([
        d.quantity_liters * d.price_per_liter
        for d in deliveries if not d.is_paid
    ])

    context = {
        'deliveries': deliveries,
        'total_litres': total_litres,
        'unpaid_amount': unpaid_amount,
    }
    return render(request, 'farmer/pages/farmer_dashboard.html', context)
