from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Payment
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Payment
from django.contrib.auth.decorators import login_required

@login_required
def payment_statements(request):
    farmer = request.user
    statements = Payment.objects.filter(farmer=farmer).order_by('-generated_on')

    context = {
        'statements': statements,
    }
    return render(request, 'farmer/pages/payment_statements.html', context)


# export to pdf
@login_required
def export_payment_statements_pdf(request):
    farmer = request.user
    payments = Payment.objects.filter(farmer=farmer)

    template_path = 'farmer/pages/payment_statements_pdf.html'
    context = {
        'payments': payments,
        'farmer': farmer,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="payment_statements.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


# finance manager
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from django.utils import timezone
from .models import MilkPrice, Payment
from .forms import MilkPriceForm

# Restrict to Finance Manager
def is_finance_manager(user):
    return user.is_authenticated and getattr(user, 'user_type', '') == 'FM'  # Assuming 'FM' for finance manager

from django.db.models.functions import TruncMonth

@login_required
@user_passes_test(is_finance_manager)
def finance_dashboard(request):
    total_pending = Payment.objects.filter(status=Payment.PaymentStatus.PENDING).aggregate(total=Sum('amount'))['total'] or 0
    paid_this_month = Payment.objects.filter(
        status=Payment.PaymentStatus.PAID,
        generated_on__month=timezone.now().month
    ).aggregate(total=Sum('amount'))['total'] or 0
    outstanding_farmers = Payment.objects.filter(status=Payment.PaymentStatus.PENDING).values('farmer').distinct().count()
    active_milk_price = MilkPrice.objects.filter(is_active=True).first()

    # Monthly paid amounts for chart
    monthly_data = (
        Payment.objects.filter(status=Payment.PaymentStatus.PAID)
        .annotate(month=TruncMonth('generated_on'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    months = [item['month'].strftime('%b %Y') for item in monthly_data]
    totals = [float(item['total']) for item in monthly_data]

    # Pending vs Paid summary
    paid_count = Payment.objects.filter(status=Payment.PaymentStatus.PAID).count()
    pending_count = Payment.objects.filter(status=Payment.PaymentStatus.PENDING).count()

    context = {
        'total_pending': total_pending,
        'paid_this_month': paid_this_month,
        'outstanding_farmers': outstanding_farmers,
        'active_milk_price': active_milk_price,
        'months': months,
        'totals': totals,
        'paid_count': paid_count,
        'pending_count': pending_count
    }
    return render(request, 'finance_manager/pages/dashboard.html', context)

@login_required
@user_passes_test(is_finance_manager)
def milk_price_list(request):
    prices = MilkPrice.objects.all()
    return render(request, 'finance_manager/pages/milk_price_list.html', {'prices': prices})


@login_required
@user_passes_test(is_finance_manager)
def milk_price_create(request):
    if request.method == 'POST':
        form = MilkPriceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('finance_manager:milk_price_list')
    else:
        form = MilkPriceForm()
    return render(request, 'finance_manager/pages/milk_price_form.html', {'form': form})


@login_required
@user_passes_test(is_finance_manager)
def payment_list(request):
    payments = Payment.objects.select_related('farmer').order_by('-generated_on')
    return render(request, 'finance_manager/pages/payment_list.html', {'payments': payments})


@login_required
@user_passes_test(is_finance_manager)
def payment_detail(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    return render(request, 'finance_manager/pages/payment_detail.html', {'payment': payment})


@login_required
@user_passes_test(is_finance_manager)
def mark_payment_paid(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if payment.status == Payment.PaymentStatus.PAID:
        messages.info(request, "This payment is already marked as paid.")
    else:
        payment.status = Payment.PaymentStatus.PAID
        payment.save()
        messages.success(request, f"Payment {payment.reference} marked as PAID.")

    return redirect("payments:payment_detail", payment.id)


@login_required
@user_passes_test(is_finance_manager)
def payments_reports(request):
    monthly_summary = Payment.objects.filter(status=Payment.PaymentStatus.PAID).extra(
        select={'month': "strftime('%%m', generated_on)"}
    ).values('month').annotate(total=Sum('amount'))

    return render(request, 'finance_manager/pages/payments_reports.html', {'monthly_summary': monthly_summary})




@login_required
def pending_payments(request):
    """
    Show all pending payments for the finance manager.
    """
    payments = Payment.objects.filter(status="pending").select_related("farmer")

    context = {
        "payments": payments
    }
    return render(request, "finance_manager/pages/pending_payments.html", context)



from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from django.http import HttpResponse
from .models import Payment


def export_payments_pdf(request):
    # Prepare HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="payments_report.pdf"'

    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title = Paragraph("Payments Report", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Table header
    data = [["Farmer Name", "Farmer ID", "Reference", "Amount (KES)", "Status", "Date"]]

    # Query payments
    payments = Payment.objects.select_related("farmer").all()

    for payment in payments:
        data.append([
            payment.farmer.get_full_name() if payment.farmer else "N/A",
            getattr(payment.farmer, "farmer_id", "N/A"),
            payment.reference,
            f"{payment.amount:.2f}",
            payment.status.capitalize(),
            payment.generated_on.strftime("%Y-%m-%d"),
        ])

    # Create table
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    doc.build(elements)

    return response

def add_milk_price(request):
    if request.method == "POST":
        form = MilkPriceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Milk price added successfully ✅")
            return redirect("payments:milk_price_list")
        else:
            messages.error(request, "Please fix the errors below ❌")
    else:
        form = MilkPriceForm()

    return render(request, "finance_manager/pages/add_milk_price.html", {"form":form})


from django.contrib import messages
def edit_milk_price(request, pk):
    price = get_object_or_404(MilkPrice, pk=pk)

    if request.method == "POST":
        form = MilkPriceForm(request.POST, instance=price)
        if form.is_valid():
            form.save()
            messages.success(request, "Milk price updated successfully ✅")
            return redirect("payments:milk_price_list")
        else:
            messages.error(request, "Please correct the errors below ❌")
    else:
        form = MilkPriceForm(instance=price)

    return render(request, "finance_manager/pages/edit_milk_price.html", {"form": form, "price": price})


def delete_milk_price(request, pk):
    price = get_object_or_404(MilkPrice, pk=pk)
    price.delete()
    messages.success(request, "Milk price deleted successfully ✅")
    return redirect("payments:milk_price_list")




    # payments/views.py
from django.db.models import Sum
from django.utils.timezone import now
import calendar
from datetime import date
from django.utils.crypto import get_random_string
from decimal import Decimal
from deliveries.models import MilkCollection

@login_required
def create_payment(request):
    """
    Auto-generate monthly payments for a farmer.
    One payment per month based on milk collected.
    """
    if request.method == "POST":
        farmer_id = request.POST.get("farmer")

        if not farmer_id:
            messages.error(request, "Please select a farmer.")
            return redirect("payments:create_payment")

        # Get all milk collections for this farmer not already linked to a payment
        collections = MilkCollection.objects.filter(
            farmer_id=farmer_id,
            payments=None  # not yet linked to payment
        ).order_by("collection_date")

        if not collections.exists():
            messages.warning(request, "No pending milk collections found for this farmer.")
            return redirect("payments:create_payment")

        # Get current milk price
        milk_price = MilkPrice.objects.filter(is_active=True).first()
        if not milk_price:
            messages.error(request, "No active milk price set.")
            return redirect("payments:create_payment")

        # Group collections by year & month
        grouped = {}
        for c in collections:
            key = (c.collection_date.year, c.collection_date.month)
            grouped.setdefault(key, []).append(c)

        created_payments = []

        for (year, month), colls in grouped.items():
            start_date = date(year, month, 1)
            end_date = date(year, month, calendar.monthrange(year, month)[1])

            total_liters = sum([c.quantity_liters for c in colls])
            amount = Decimal(total_liters) * milk_price.price_per_liter

            payment = Payment.objects.create(
                farmer_id=farmer_id,
                start_date=start_date,
                end_date=end_date,
                amount=amount,
                status=Payment.PaymentStatus.PENDING,
                reference=f"PAY-{get_random_string(8).upper()}"
            )
            payment.milk_collections.set(colls)
            created_payments.append(payment)

        if created_payments:
            messages.success(
                request,
                f"{len(created_payments)} monthly payment(s) generated for farmer."
            )
            return redirect("payments:payment_list")  # redirect to list view
        else:
            messages.info(request, "No new payments were generated.")
            return redirect("payments:create_payment")

    # If GET → Show farmers
    farmers = Payment.farmer.field.related_model.objects.filter(user_type="FR")
    return render(request, "finance_manager/pages/create_payment.html", {"farmers": farmers})


