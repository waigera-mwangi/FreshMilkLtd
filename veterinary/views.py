from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.contrib import messages
from django.urls import reverse
from accounts.views import veterinary

@login_required
def request_vet_service(request):
    if request.method == 'POST':
        form = VetServiceRequestForm(request.POST)
        if form.is_valid():
            vet_request = form.save(commit=False)
            vet_request.farmer = request.user
            vet_request.save()
            return redirect('veterinary:farmer_vet_requests')  # URL to list view
    else:
        form = VetServiceRequestForm()
    
    return render(request, 'farmer/pages/request_vet_service.html', {'form': form})


@login_required
def farmer_vet_requests_list(request):
    vet_requests = VetServiceRequest.objects.filter(farmer=request.user)
    return render(request, 'farmer/pages/vet_requests.html', {
        'vet_requests': vet_requests
    })

def about_us(request):
    return render(request, 'farmer/pages/about_us.html')

# veterinary
# View: List of assigned requests
@login_required
def vet_dashboard(request):
    pending_requests = VetServiceRequest.objects.filter(vet_officer=request.user, status='PENDING').count()
    approved_requests = VetServiceRequest.objects.filter(vet_officer=request.user, status='APPROVED').count()
    completed_treatments = VetTreatmentRecord.objects.filter(request__vet_officer=request.user).count()

    context = {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'completed_treatments': completed_treatments,
    }
    return render(request, 'veterinary/pages/index.html', context)


@login_required
def assigned_requests(request):
    requests = VetServiceRequest.objects.filter(vet_officer=request.user)
    return render(request, 'veterinary/pages/assigned_requests.html', {'requests': requests})

# View: Update request status
@login_required
def update_request(request, pk):
    vet_request = get_object_or_404(VetServiceRequest, pk=pk, vet_officer=request.user)

    if request.method == 'POST':
        form = VetServiceRequestUpdateForm(request.POST, instance=vet_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service request updated.')
            return redirect('veterinary:assigned_requests')
    else:
        form = VetServiceRequestUpdateForm(instance=vet_request)

    return render(request, 'veterinary/pages/update_request.html', {'form': form, 'vet_request': vet_request})

# View: Add treatment record
@login_required
def add_treatment_record(request, pk):
    vet_request = get_object_or_404(VetServiceRequest, pk=pk, vet_officer=request.user)

    if hasattr(vet_request, 'treatment_record'):
        messages.warning(request, 'Treatment record already exists.')
        return redirect('veterinary:assigned_requests')

    if request.method == 'POST':
        form = VetTreatmentRecordForm(request.POST)
        if form.is_valid():
            treatment = form.save(commit=False)
            treatment.request = vet_request
            treatment.save()
            messages.success(request, 'Treatment record added.')
            return redirect('veterinary:assigned_requests')
    else:
        form = VetTreatmentRecordForm()

    return render(request, 'veterinary/pages/add_treatment_record.html', {'form': form, 'vet_request': vet_request})

login_required
def treatment_record_list(request):
    records = VetTreatmentRecord.objects.filter(request__vet_officer=request.user)
    return render(request, 'veterinary/pages/treatment_record_list.html', {'records': records})