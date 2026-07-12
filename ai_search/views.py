from urllib.parse import urlencode

from django.shortcuts import redirect, render
from django.urls import reverse

from .assistant import (
    assistant_suggestions,
    get_or_create_conversation,
    handle_user_message,
    recent_conversations,
    reset_conversation,
    start_conversation,
    generate_assistant_reply_only,
)
from .forms import TutorSearchForm
from .services import extract_search_intent, search_tutors, suggested_prompts


def find_tutor(request):
    query = request.GET.get("q", "").strip()
    if query:
        return redirect(f"{reverse('ai_assistant')}?{urlencode({'q': query})}")
    return redirect("ai_assistant")


def ai_assistant(request):
    conversation_id = request.GET.get("conversation")
    conversation = get_or_create_conversation(request, conversation_id=conversation_id)

    if request.GET.get("reset") == "1":
        conversation = reset_conversation(request)

    initial_prompt = request.GET.get("q", "").strip()
    start_conversation(conversation, initial_prompt)

    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        generate_only = request.POST.get("generate_only") == "1"
        
        if generate_only:
            generate_assistant_reply_only(conversation)
        else:
            if message:
                handle_user_message(conversation, message)
        return redirect(f"{reverse('ai_assistant')}?{urlencode({'conversation': conversation.id})}")

    chat_messages = conversation.messages.all()
    latest_assistant = chat_messages.filter(role="assistant").last()
    latest_tutors = []
    if latest_assistant:
        latest_tutors = latest_assistant.metadata.get("tutors", [])

    return render(
        request,
        "search/ai_assistant.html",
        {
            "conversation": conversation,
            "chat_messages": chat_messages,
            "latest_tutors": latest_tutors,
            "suggested_prompts": assistant_suggestions(),
            "recent_conversations": recent_conversations(request, request.GET.get("chat_search", "")),
            "chat_search": request.GET.get("chat_search", ""),
        },
    )



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


def delete_conversation(request, conversation_id):
    from .models import AIConversation
    from django.shortcuts import get_object_or_404

    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        conversation = get_object_or_404(AIConversation, id=conversation_id, user=request.user)
    else:
        conversation = get_object_or_404(AIConversation, id=conversation_id, session_key=request.session.session_key)

    conversation.delete()
    return redirect("ai_assistant")
