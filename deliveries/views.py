from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.db.models import Sum
from django.utils.dateformat import DateFormat
from collections import defaultdict
from decimal import Decimal
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from .forms import *
from django.contrib import messages
from datetime import date
from django.db import models

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

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

#  field agent views
from datetime import date, timedelta
from django.db.models import Sum
from django.shortcuts import render
from .models import MilkCollection

def dashboard(request):
    # Filter by the logged-in field agent if you want personalized stats
    milk_qs = MilkCollection.objects.all()
    if request.user.is_authenticated and hasattr(request.user, 'user_type') and request.user.user_type == 'FIELD_AGENT':
        milk_qs = milk_qs.filter(field_agent=request.user)

    # Total milk collected
    milk_collected = milk_qs.aggregate(total=Sum('quantity_liters'))['total'] or 0

    # Milk collected per day for the last 7 days
    last_7_days = (
        milk_qs
        .filter(collection_date__gte=date.today() - timedelta(days=6))
        .values('collection_date')
        .annotate(total=Sum('quantity_liters'))
        .order_by('collection_date')
    )

    labels = [entry['collection_date'].strftime("%b %d") for entry in last_7_days]
    data = [entry['total'] for entry in last_7_days]

    return render(request, 'field_agent/dashboard.html', {
        'milk_collected': milk_collected,
        'chart_labels': labels,
        'chart_data': data,
    })



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_GET, require_POST
from django.utils.timezone import now
from .models import MilkCollection
from .forms import MilkCollectionForm

User = get_user_model()

@require_GET
def get_farmer_name(request):
    farmer_id = request.GET.get("farmer_id", "").strip()
    try:
        farmer = User.objects.get(farmer_id=farmer_id, user_type=User.UserTypes.FARMER)
        return JsonResponse({"name": farmer.get_full_name()})
    except User.DoesNotExist:
        return JsonResponse({"name": ""}, status=404)


def record_collection(request):
    if request.method == 'POST':
        form = MilkCollectionForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Milk collection recorded successfully!'
                })
            return redirect('deliveries:record_collection')  # normal redirect for non-AJAX
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = MilkCollectionForm()

    return render(request, 'field_agent/pages/record_collection.html', {'form': form})

@login_required
def milk_collection_list(request):
    collections = MilkCollection.objects.all().order_by('-collection_date')
    return render(request, 'field_agent/pages/milk_collection_list.html', {'collections': collections})




# field manager


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from django.utils import timezone

def is_field_manager(user):
    return user.is_authenticated and user.user_type == 'FD'


@login_required
@user_passes_test(is_field_manager)
def manager_dashboard(request):
    today = timezone.now().date()

    # Stats
    total_milk_today = MilkCollection.objects.filter(collection_date=today).aggregate(
        total=Sum('quantity_liters')
    )['total'] or 0

    total_milk_month = MilkCollection.objects.filter(
        collection_date__month=today.month,
        collection_date__year=today.year
    ).aggregate(total=Sum('quantity_liters'))['total'] or 0

    total_unpaid = MilkCollection.objects.filter(is_paid=False).aggregate(
        total=Sum('quantity_liters')
    )['total'] or 0

    total_agents = User.objects.filter(user_type='FA').count()
    active_locations = PickupLocation.objects.filter(is_active=True).count()

    recent_collections = MilkCollection.objects.select_related('farmer', 'pickup_location')[:10]
    recent_supervisions = FieldSupervision.objects.select_related('manager', 'field_agent').order_by('-supervision_date')[:5]

    context = {
        "total_milk_today": total_milk_today,
        "total_milk_month": total_milk_month,
        "total_unpaid": total_unpaid,
        "total_agents": total_agents,
        "active_locations": active_locations,
        "recent_collections": recent_collections,
        "recent_supervisions": recent_supervisions,
    }
    return render(request, "field_manager/pages/dashboard.html", context)


@login_required
@user_passes_test(is_field_manager)
def pickup_locations(request):
    locations = PickupLocation.objects.all()
    return render(request, "field_manager/pages/pickup_locations.html", {"locations": locations})


@login_required
@user_passes_test(is_field_manager)
def add_pickup_location(request):
    """Add new pickup location"""
    if request.method == "POST":
        form = PickupLocationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Pickup location added successfully.")
            return redirect("deliveries:pickup_locations")
    else:
        form = PickupLocationForm()
    return render(request, "field_manager/pages/add_pickup_location.html", {"form": form})


@login_required
@user_passes_test(is_field_manager)
def edit_pickup_location(request, pk):
    """Edit existing pickup location"""
    location = get_object_or_404(PickupLocation, pk=pk)
    if request.method == "POST":
        form = PickupLocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, "Pickup location updated successfully.")
            return redirect("deliveries:pickup_locations")
    else:
        form = PickupLocationForm(instance=location)
    return render(request, "field_manager/pages/edit_pickup_location.html", {"form": form, "location": location})


@login_required
@user_passes_test(is_field_manager)
def delete_pickup_location(request, pk):
    """Delete pickup location"""
    location = get_object_or_404(PickupLocation, pk=pk)
    if request.method == "POST":
        location.delete()
        messages.success(request, "Pickup location deleted successfully.")
        return redirect("deliveries:pickup_locations")
    return render(request, "field_manager/pages/confirm_delete_pickup_location.html", {"location": location})

@login_required
@user_passes_test(is_field_manager)
def milk_collections_report(request):
    collections = MilkCollection.objects.select_related("farmer", "pickup_location").order_by("-collection_date")

    summary = collections.values("pickup_location__name").annotate(
        total=Sum("quantity_liters"), count=Count("id")
    )

    return render(request, "field_manager/pages/milk_collections_report.html", {
        "collections": collections,
        "summary": summary
    })

@login_required
@user_passes_test(is_field_manager)
def supervisions(request):
    supervisions = FieldSupervision.objects.select_related("manager", "field_agent").order_by("-supervision_date")
    return render(request, "field_manager/pages/supervisions.html", {"supervisions": supervisions})


@login_required
@user_passes_test(is_field_manager)
def add_supervision(request):
    if request.method == "POST":
        form = FieldSupervisionForm(request.POST)
        if form.is_valid():
            supervision = form.save(commit=False)
            supervision.manager = request.user  # assign logged-in manager
            supervision.save()
            messages.success(request, "Supervision added successfully.")
            return redirect("deliveries:supervisions")
    else:
        form = FieldSupervisionForm()
    return render(request, "field_manager/pages/add_supervision.html", {"form": form})


@login_required
@user_passes_test(is_field_manager)
def edit_supervision(request, pk):
    supervision = get_object_or_404(FieldSupervision, pk=pk)
    if request.method == "POST":
        form = FieldSupervisionForm(request.POST, instance=supervision)
        if form.is_valid():
            form.save()
            messages.success(request, "Supervision updated successfully.")
            return redirect("deliveries:supervisions")
    else:
        form = FieldSupervisionForm(instance=supervision)
    return render(request, "field_manager/pages/edit_supervision.html", {"form": form, "supervision": supervision})


@login_required
@user_passes_test(is_field_manager)
def delete_supervision(request, pk):
    supervision = get_object_or_404(FieldSupervision, pk=pk)
    if request.method == "POST":
        supervision.delete()
        messages.success(request, "Supervision deleted successfully.")
        return redirect("deliveries:supervisions")
    return render(request, "field_manager/pages/delete_supervision.html", {"supervision": supervision})

@login_required
@user_passes_test(is_field_manager)
def farmers_list(request):
    farmers = User.objects.filter(user_type="FR").order_by("first_name", "last_name")
    return render(request, "field_manager/pages/farmers_list.html", {"farmers": farmers})


@login_required
@user_passes_test(is_field_manager)
def farmer_detail(request, farmer_id):
    farmer = get_object_or_404(User, pk=farmer_id, user_type="FR")
    milk_collections = farmer.milk_collections.select_related("pickup_location").order_by("-collection_date")
    return render(request, "field_manager/pages/farmer_detail.html", {
        "farmer": farmer,
        "milk_collections": milk_collections
    })



@user_passes_test(is_field_manager)
def milk_collections_report(request):
    # Aggregate total milk per farmer
    farmer_report = (
        MilkCollection.objects.values("farmer__first_name", "farmer__last_name")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")
    )

    # Aggregate per pickup location
    location_report = (
        MilkCollection.objects.values("pickup_location__name")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")
    )

    # Aggregate per date (daily totals)
    daily_report = (
        MilkCollection.objects.values("collection_date")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-collection_date")
    )

    context = {
        "farmer_report": farmer_report,
        "location_report": location_report,
        "daily_report": daily_report,
    }
    return render(request, "field_manager/pages/milk_collections_report.html", context)