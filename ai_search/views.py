from urllib.parse import urlencode

from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import TutorSearchForm
from .services import extract_search_intent, search_tutors, suggested_prompts


def find_tutor(request):
    query = request.GET.get("q", "").strip()
    if query:
        return redirect(f"{reverse('search_results')}?{urlencode({'q': query})}")
    return redirect('search_results')



def search_results(request):
    from django.contrib import messages
    from urllib.parse import quote
    
    form = TutorSearchForm(request.GET)
    query = request.GET.get("q", "").strip()
    
    if not query:
        messages.warning(request, "Please enter a subject, level, or location to find a tutor.")
        return redirect('home')

    filters = {}
    if form.is_valid():
        filters = {
            "subject": form.cleaned_data.get("subject"),
            "location": form.cleaned_data.get("location"),
            "min_price": form.cleaned_data.get("min_price"),
            "max_price": form.cleaned_data.get("max_price"),
            "min_experience": form.cleaned_data.get("min_experience"),
        }

    intent = extract_search_intent(query)
    tutors = search_tutors(intent, filters)

    if not tutors:
        messages.error(request, f"No tutors found matching '{query}'. Try searching for a subject like 'Mathematics' or location like 'GRA', or use voice search!")
        return redirect(f"/?q={quote(query)}")

    return render(
        request,
        "search/search_results.html",
        {
            "form": form,
            "query": query,
            "intent": intent,
            "tutors": tutors,
            "suggested_prompts": suggested_prompts(),
        },
    )
