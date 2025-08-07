from django.shortcuts import render, redirect
from .models import FAQ, Feedback
from .forms import FeedbackForm
from django.contrib.auth.decorators import login_required

def faq_list(request):
    faqs = FAQ.objects.all()
    return render(request, 'farmer/support/faq.html', {'faqs': faqs})

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            return redirect('support:thank_you')
    else:
        form = FeedbackForm()
    
    return render(request, 'farmer/support/feedback.html', {'form': form})

def thank_you(request):
    return render(request, 'farmer/support/thank_you.html')

