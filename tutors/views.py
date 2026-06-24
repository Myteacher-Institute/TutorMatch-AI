from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from accounts.decorators import tutor_required
from .models import Tutor

@tutor_required
def tutor_dashboard(request):
    # Retrieve the Tutor instance associated with the logged-in user's UserProfile
    # If the user doesn't have a tutor profile yet, this will return a 404 error
    tutor_profile = get_object_or_404(Tutor, user=request.user)
    
    context = {
        'tutor': tutor_profile,
    }
    
    # Points to templates/tutors/tutor_dashboard.html
    return render(request, 'tutors/tutor_dashboard.html', context)

# Keep your other placeholders as-is for now until you build their templates
def tutor_profile(request):
    return HttpResponse("Tutor profile page will be built by Task 3.")

def tutor_verification(request):
    return HttpResponse("Tutor verification page will be built by Task 3.")

def tutor_list(request):
    return HttpResponse("Tutor listings will be built by Task 3.")

def tutor_detail(request, tutor_id):
    return HttpResponse(f"Tutor profile {tutor_id} will be built by Task 3.")