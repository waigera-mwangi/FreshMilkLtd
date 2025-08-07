from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import VetServiceRequestForm
from .models import VetServiceRequest

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