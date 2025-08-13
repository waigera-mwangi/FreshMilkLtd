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
def vet_service_requests(request):
    vet_requests = VetServiceRequest.objects.filter(
        status=VetServiceRequest.RequestStatus.PENDING,
        vet_officer__isnull=True
    ).order_by('-request_date')

    return render(request, 'veterinary/pages/vet_requests.html', {
        'vet_requests': vet_requests
    })
    
    
@login_required
def claim_vet_request(request, request_id):
    try:
        vet_request = VetServiceRequest.objects.get(id=request_id)
    except VetServiceRequest.DoesNotExist:
        messages.error(request, "The vet request you are trying to claim does not exist.")
        return redirect('veterinary:vet_service_requests')

    # Already claimed?
    if vet_request.vet_officer is not None:
        messages.error(request, "This request has already been claimed by another vet.")
        return redirect('veterinary:vet_service_requests')

    # Must still be pending to claim
    if vet_request.status != VetServiceRequest.RequestStatus.PENDING:
        messages.error(request, "This request is no longer available for claiming.")
        return redirect('veterinary:vet_service_requests')

    # Assign to current vet
    vet_request.vet_officer = request.user
    vet_request.status = VetServiceRequest.RequestStatus.APPROVED
    vet_request.save()

    messages.success(request, "You have successfully claimed this request.")
    return redirect('veterinary:vet_treatment_record_create', request_id=request_id)


@login_required
def assigned_requests(request):
    assigned = VetServiceRequest.objects.filter(
        vet_officer=request.user
    ).exclude(status=VetServiceRequest.RequestStatus.COMPLETED)
    return render(request, 'veterinary/pages/assigned_requests.html', {
        'assigned_requests': assigned
    })

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
def add_treatment_record(request, request_id):
    vet_request = get_object_or_404(
        VetServiceRequest,
        id=request_id,
        vet_officer=request.user
    )

    if request.method == 'POST':
        form = VetTreatmentRecordForm(request.POST)
        if form.is_valid():
            treatment = form.save(commit=False)
            treatment.vet_request = vet_request
            treatment.save()

            # Mark the request as completed
            vet_request.status = VetServiceRequest.RequestStatus.COMPLETED
            vet_request.save()

            messages.success(request, "Treatment record saved and request marked as completed.")
            return redirect('veterinary:assigned_requests')
    else:
        form = VetTreatmentRecordForm()

    return render(request, 'veterinary/pages/add_treatment_record.html', {
        'form': form,
        'vet_request': vet_request
    })

@login_required
def vet_treatment_record_create(request, request_id):
    service_request = get_object_or_404(VetServiceRequest, id=request_id)

    if request.method == "POST":
        form = VetTreatmentRecordForm(request.POST)
        if form.is_valid():
            treatment_record = form.save(commit=False)
            treatment_record.service_request = service_request
            treatment_record.vet = request.user  # assuming the logged-in user is the vet
            treatment_record.save()

            # Optionally update request status
            service_request.status = "Completed"
            service_request.save()

            return redirect("veterinary:vet_service_requests")  # or wherever you want to go
    else:
        form = VetTreatmentRecordForm()

    return render(request, "veterinary/pages/vet_treatment_record_form.html", {
        "form": form,
        "service_request": service_request,
    })
    
    

login_required
def treatment_record_list(request, request_id):
    vet_request = get_object_or_404(VetServiceRequest, id=request_id)
    records = VetTreatmentRecord.objects.filter(vet_request=vet_request)
    return render(request, 'veterinary/pages/treatment_record_list.html', {
        'vet_request': vet_request,
        'records': records
    })