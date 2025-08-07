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
