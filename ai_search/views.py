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
    detect_navigation_intent,
)
from .forms import TutorSearchForm
from .services import extract_search_intent, search_tutors, suggested_prompts


def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def _assistant_context(request, conversation):
    chat_messages = conversation.messages.all()
    latest_assistant = chat_messages.filter(role="assistant").last()
    latest_tutors = []
    if latest_assistant:
        latest_tutors = latest_assistant.metadata.get("tutors", [])

    return {
        "conversation": conversation,
        "chat_messages": chat_messages,
        "latest_tutors": latest_tutors,
        "suggested_prompts": assistant_suggestions(),
        "recent_conversations": recent_conversations(request, request.GET.get("chat_search", "")),
        "chat_search": request.GET.get("chat_search", ""),
    }


def find_tutor(request):
    query = request.GET.get("q", "").strip()
    if query:
        return redirect(f"{reverse('ai_assistant')}?{urlencode({'reset': '1', 'q': query})}")
    return redirect(f"{reverse('ai_assistant')}?reset=1")


def ai_assistant(request, conversation_id=None):
    if conversation_id is None:
        initial_prompt = request.GET.get("q", "").strip()
        if request.GET.get("reset") == "1" or initial_prompt:
            conversation = reset_conversation(request)
        else:
            active_id = request.session.get("ai_conversation_id")
            conversation = None
            if active_id:
                from .models import AIConversation
                try:
                    conversation = AIConversation.objects.filter(id=active_id).first()
                except Exception:
                    pass
            if not conversation:
                conversation = reset_conversation(request)

        url = reverse("ai_assistant_thread", kwargs={"conversation_id": conversation.id})
        query_params = request.GET.copy()
        if "reset" in query_params:
            del query_params["reset"]
        if query_params:
            url = f"{url}?{urlencode(query_params)}"
        return redirect(url)

    from .models import AIConversation
    from django.shortcuts import get_object_or_404

    if request.user.is_authenticated:
        conversation = get_object_or_404(AIConversation, id=conversation_id, user=request.user)
    else:
        conversation = get_object_or_404(AIConversation, id=conversation_id, session_key=request.session.session_key)

    request.session["ai_conversation_id"] = str(conversation.id)

    initial_prompt = request.GET.get("q", "").strip()
    if start_conversation(conversation, initial_prompt):
        generate_assistant_reply_only(conversation)
        conversation.refresh_from_db()

    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        generate_only = request.POST.get("generate_only") == "1"

        # Check if user is asking to navigate somewhere
        nav_path = detect_navigation_intent(message)
        if nav_path:
            return redirect(nav_path)

        if generate_only:
            generate_assistant_reply_only(conversation)
        else:
            if message:
                handle_user_message(conversation, message)
        if _is_ajax(request):
            conversation.refresh_from_db()
            return render(request, "search/ai_assistant.html", _assistant_context(request, conversation))
        return redirect(reverse("ai_assistant_thread", kwargs={"conversation_id": conversation.id}))

    return render(request, "search/ai_assistant.html", _assistant_context(request, conversation))



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

    if request.session.get("ai_conversation_id") == str(conversation.id):
        del request.session["ai_conversation_id"]

    conversation.delete()
    return redirect("ai_assistant")
