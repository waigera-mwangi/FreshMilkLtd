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
def mark_payment_paid(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    payment.status = Payment.PaymentStatus.PAID
    payment.save()
    return redirect('payments:payment_list')


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