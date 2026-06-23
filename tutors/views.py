from django.http import HttpResponse
from accounts.decorators import tutor_required


@tutor_required
def tutor_dashboard(request):
    return HttpResponse("Tutor dashboard will be built by Task 3.")


def tutor_profile(request):
    return HttpResponse("Tutor profile page will be built by Task 3.")


def tutor_verification(request):
    return HttpResponse("Tutor verification page will be built by Task 3.")


def tutor_list(request):
    return HttpResponse("Tutor listings will be built by Task 3.")


def tutor_detail(request, tutor_id):
    return HttpResponse(f"Tutor profile {tutor_id} will be built by Task 3.")
