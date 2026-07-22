import json
import logging
import os
import time
from django.db import transaction
from django.utils import timezone

from .models import AIMessage, AdminAlert
from .services import extract_search_intent, search_tutors, suggested_prompts

logger = logging.getLogger(__name__)


ASSISTANT_INSTRUCTIONS = """
You are Myteacher AI, a warm conversational tutor-matching and learning assistant for students and parents in Nigeria.

Your job:
- Have a natural conversation, not a one-shot search.
- Ask one useful follow-up question at a time when details are missing.
- Collect: subject/course/skill, student age or class level where relevant, location, learning goal, schedule, budget, and whether online or home tutoring is preferred.
- Primary goal: recommend tutors from our database once the user's need is clear enough.
- When tutor matches are provided, recommend the best options by name and explain why they fit the conversation.
- If there are no tutor matches yet, refine the tutor search by asking for location, preferred format, budget, or permission to broaden nearby/online tutors.
- Help with assignments by guiding and explaining. Do not simply do all assessed work for the student.
- Do not offer a structured online curriculum as the main next step while the user is trying to find a tutor. Mention learning paths only after tutor options are shown or if the user explicitly asks for curriculum/course guidance.
- Be concise, friendly, and practical. Use Nigerian context where helpful.
- When the user has not provided a topic yet, ask: "What subject, course, or skill do you want help in finding the right tutor? For example Mathematics, Python, C++, CSS, HTML, WAEC, or JAMB."
- If the user asks for more tutor suggestions and has already seen several batches (tutor_page >= 3), output exactly: NAVIGATE: /tutors/

SPECIAL COMMANDS (respond only with "NAVIGATE: /path" when user asks):
- If user asks "take me to tutors", "go to find tutors", "show me tutors page" → respond with: NAVIGATE: /tutors/
- If user asks "show dashboard", "go to dashboard" → respond with: NAVIGATE: /dashboard/
- If user asks "go to home", "home page", "main page" → respond with: NAVIGATE: /
- If user asks "go to bookings", "show my bookings" → respond with: NAVIGATE: /bookings/
- If user asks "show my chats", "go to chats" → respond with: NAVIGATE: /chat/
"""


REQUIRED_MATCH_FIELDS = ["subject", "location", "mode"]


def get_or_create_conversation(request, conversation_id=None):
    from .models import AIConversation

    if not request.session.session_key:
        request.session.create()

    conversation_id = conversation_id or request.session.get("ai_conversation_id")
    queryset = AIConversation.objects.all()

    if request.user.is_authenticated:
        conversation = queryset.filter(id=conversation_id, user=request.user).first()
        if conversation:
            return conversation
        conversation = AIConversation.objects.create(user=request.user, session_key=request.session.session_key)
    else:
        conversation = queryset.filter(id=conversation_id, session_key=request.session.session_key).first()
        if conversation:
            return conversation
        conversation = AIConversation.objects.create(session_key=request.session.session_key)

    request.session["ai_conversation_id"] = str(conversation.id)
    return conversation


def reset_conversation(request):
    from .models import AIConversation

    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        conversation = AIConversation.objects.create(user=request.user, session_key=request.session.session_key)
    else:
        conversation = AIConversation.objects.create(session_key=request.session.session_key)

    request.session["ai_conversation_id"] = str(conversation.id)
    return conversation


def recent_conversations(request, search_query=""):
    from .models import AIConversation

    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        conversations = AIConversation.objects.filter(user=request.user)
    else:
        conversations = AIConversation.objects.filter(session_key=request.session.session_key)

    results = []
    search_query = (search_query or "").strip().lower()
    for conversation in conversations.prefetch_related("messages")[:20]:
        first_user_message = next((msg.content for msg in conversation.messages.all() if msg.role == AIMessage.ROLE_USER), "")
        title = first_user_message or "New chat"
        if search_query and search_query not in title.lower():
            continue
        results.append({"id": conversation.id, "title": title[:58]})
        if len(results) >= 8:
            break
    return results


def start_conversation(conversation, initial_prompt=""):
    if initial_prompt and not conversation.messages.exists():
        AIMessage.objects.create(conversation=conversation, role=AIMessage.ROLE_USER, content=initial_prompt.strip())
        return True
    return False


def handle_user_message(conversation, user_text):
    user_text = (user_text or "").strip()
    if not user_text:
        return None

    AIMessage.objects.create(conversation=conversation, role=AIMessage.ROLE_USER, content=user_text)
    return generate_assistant_reply_only(conversation)


def generate_assistant_reply_only(conversation):
    # Use a database transaction and row-level lock to avoid race conditions
    from .models import AIConversation

    with transaction.atomic():
        locked_conv = AIConversation.objects.select_for_update().get(id=conversation.id)

        # 1. Pre-API check: if the last message is already an assistant message, skip
        last_msg = locked_conv.messages.order_by("created_at").last()
        if last_msg and last_msg.role == AIMessage.ROLE_ASSISTANT:
            return last_msg

        import os
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        if not os.getenv("GEMINI_API_KEY"):
            state = {}
            tutors = []
            assistant_text = "AI not available at the moment thank you"
        else:
            state = _merge_state(locked_conv)
            tutors = _recommend_tutors(state)
            assistant_text = _generate_assistant_reply(locked_conv, state, tutors)
            if not (assistant_text or "").strip():
                assistant_text = _generate_fallback_reply(state, tutors)

        # 2. Post-API check: if another concurrent request already created the assistant message, skip
        last_msg = locked_conv.messages.order_by("created_at").last()
        if last_msg and last_msg.role == AIMessage.ROLE_ASSISTANT:
            # If identical content already exists, return it; otherwise skip creating a duplicate
            if last_msg.content and last_msg.content.strip() == assistant_text.strip():
                return last_msg
            return last_msg

        assistant_message = AIMessage.objects.create(
            conversation=locked_conv,
            role=AIMessage.ROLE_ASSISTANT,
            content=assistant_text,
            metadata={"tutors": tutors[:3], "state": state},
        )
        locked_conv.state = state
        locked_conv.save(update_fields=["state", "updated_at"])
        return assistant_message


def _merge_state(conversation):
    previous_state = conversation.state or {}
    user_messages = list(
        conversation.messages.filter(role=AIMessage.ROLE_USER)
        .order_by("created_at")
        .values_list("content", flat=True)
    )

    profile_location = ""
    if conversation.user:
        try:
            tutor_profile = conversation.user.tutor_profile
            if tutor_profile and tutor_profile.location:
                profile_location = tutor_profile.location
        except:
            pass

    return _merge_intent_state(previous_state, user_messages, profile_location)


def _merge_intent_state(previous_state, user_messages, profile_location=""):
    latest_user_text = user_messages[-1] if user_messages else ""
    conversation_text = "\n".join(user_messages)
    latest_intent = extract_search_intent(latest_user_text)
    context_intent = extract_search_intent(conversation_text) if len(user_messages) > 1 else latest_intent

    previous_subject = previous_state.get("subject", "")
    latest_subject = latest_intent.get("subject", "")
    subject_changed = bool(
        latest_subject
        and previous_subject
        and latest_subject.lower() != previous_subject.lower()
    )

    location = (
        latest_intent.get("location")
        or previous_state.get("location")
        or context_intent.get("location", "")
        or profile_location
    )

    tutor_page = previous_state.get("tutor_page", 0)
    if latest_intent.get("wants_more", False):
        tutor_page += 1
    
    if subject_changed:
        tutor_page = 0

    state = {
        "query_text": latest_user_text,
        "conversation_text": conversation_text,
        "subject": latest_subject or previous_subject,
        "level": latest_intent.get("level") or ("" if subject_changed else previous_state.get("level", "")),
        "location": location,
        "schedule": latest_intent.get("schedule") or previous_state.get("schedule", "") or context_intent.get("schedule", ""),
        "mode": latest_intent.get("mode") or previous_state.get("mode", "") or context_intent.get("mode", ""),
        "tutor_page": tutor_page,
        "source": latest_intent.get("source", "fallback"),
    }
    state["missing_fields"] = [field for field in REQUIRED_MATCH_FIELDS if not state.get(field)]
    state["ready_for_tutor_match"] = not state["missing_fields"]
    state["learning_mode"] = _detect_learning_mode(latest_user_text)
    return state


def _recommend_tutors(state):
    if not state.get("ready_for_tutor_match"):
        return []
    page = state.get("tutor_page", 0)
    offset = page * 2
    return search_tutors(state, {})[offset : offset + 2]


def _generate_assistant_reply(conversation, state, tutors):
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except ImportError:
        pass

    if not os.getenv("GEMINI_API_KEY"):
        return _generate_service_error_reply()
    try:
        return _generate_gemini_reply(conversation, state, tutors)
    except Exception as e:
        logger.error("Gemini assistant response failed: %s", _safe_error_message(e))
        _create_admin_alert(e, conversation, state)
        return _generate_service_error_reply()


def _generate_gemini_reply(conversation, state, tutors):
    import requests

    api_key = os.getenv("GEMINI_API_KEY")
    configured_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from environment.")

    headers = {"Content-Type": "application/json"}

    system_text = (
        f"{ASSISTANT_INSTRUCTIONS}\n\n"
        "Current extracted student need:\n"
        f"{json.dumps(state, ensure_ascii=True)}\n\n"
        "Available tutor matches from our database:\n"
        f"{json.dumps(tutors[:5], ensure_ascii=True)}\n\n"
        "If required details are missing, ask the next best question. "
        "If tutor matches exist, recommend them by name and why they fit, and invite the user to view or book a tutor. "
        "If ready_for_tutor_match is true but the available tutor matches list is empty, it means we have no tutors for that subject right now. In this case, politely inform the user that no current tutor is offering it. Then, proactively suggest related subjects or alternative skills they might want to learn instead, based on what they originally asked for (e.g., if they asked for Python, suggest other programming languages; if Math, suggest other related subjects). Do not just say 'not found'."
    )

    contents = []
    for msg in conversation.messages.order_by("created_at")[:12]:
        role = "user" if msg.role == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg.content}]
        })

    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": system_text}]
        },
        "generationConfig": {
            "temperature": 0.4
        }
    }

    models_to_try = []
    for model in [configured_model, "gemini-2.0-flash", "gemini-flash-lite-latest", "gemini-flash-latest"]:
        if model and model not in models_to_try:
            models_to_try.append(model)

    last_error = None
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        try:
            for attempt in range(2):
                response = requests.post(
                    url,
                    params={"key": api_key},
                    json=payload,
                    headers=headers,
                    timeout=30,
                )
                if response.status_code in {429, 500, 502, 503, 504} and attempt == 0:
                    time.sleep(1)
                    continue
                response.raise_for_status()

                res_data = response.json()
                try:
                    return res_data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError, ValueError) as e:
                    logger.error(f"Failed to parse Gemini response: {res_data}", exc_info=True)
                    raise ValueError("Failed to get response from Gemini API.") from e
        except requests.exceptions.Timeout as e:
            logger.error("Gemini API timeout after 30 seconds for model %s", model)
            last_error = TimeoutError(f"Gemini model {model} did not respond within 30 seconds")
        except requests.exceptions.ConnectionError as e:
            logger.error("Gemini API connection error for model %s", model)
            last_error = ConnectionError(f"Failed to connect to Gemini model {model}")
        except requests.exceptions.HTTPError as e:
            logger.error("Gemini API HTTP error for model %s: %s", model, _safe_error_message(e))
            last_error = e

    raise last_error or ConnectionError("Failed to connect to Gemini API service")


def _generate_fallback_reply(state, tutors):
    if tutors:
        subject = state.get("subject") or "your learning goal"
        location = state.get("location") or "your area"
        lines = [
            f"I found tutor options for **{subject}** around **{location}**.",
            "",
        ]
        for tutor in tutors[:3]:
            rate_period = tutor.get("rate_period", "weekly")
            lines.append(
                f"- **{tutor['name']}** - {tutor.get('specialist', tutor['subject'])}; "
                f"{tutor['experience']} yrs experience; {tutor['location']}; "
                f"NGN {tutor['rate']}/{rate_period}."
            )
        lines.extend([
            "",
            "Pick one to view the profile or book a lesson.",
        ])
        return "\n".join(lines)

    missing = state.get("missing_fields", [])
    if "subject" in missing:
        return "What subject, course, or skill do you want help in finding the right tutor? For example Mathematics, Python, C++, CSS, HTML, WAEC, or JAMB."
    if "location" in missing:
        return "Great. What location should I search around? You can say Port Harcourt, GRA, Rumuola, Woji, or online."

    return (
        "I do not see a strong tutor match yet. Should I broaden the tutor search to nearby locations, online tutors, or related skills?"
    )


def _course_suggestion_reply(state):
    subject = state.get("subject") or "the topic"
    return (
        f"For learning {subject}, I would start with a short beginner path: fundamentals, guided practice, "
        "one small project, then review with a tutor. Tell me the student's age/class and current level, "
        "and I will suggest the next best course path."
    )


def _detect_learning_mode(text):
    lowered = (text or "").lower()
    if any(word in lowered for word in ["assignment", "homework", "solve", "explain"]):
        return "assignment"
    if any(word in lowered for word in ["learn", "course", "html", "coding", "programming"]):
        return "course"
    return "tutor_match"


def detect_navigation_intent(text):
    """
    Detect if user is asking for navigation to a specific page.
    Returns the path if a navigation command is found, otherwise None.
    """
    lowered = (text or "").lower().strip()
    
    # Navigation mappings
    nav_patterns = {
        "/tutors/": ["take me to tutor", "go to find tutor", "show me tutor", "tutor page", "find tutor", "go to tutors", "tutors page"],
        "/dashboard/": ["show dashboard", "go to dashboard", "my dashboard", "dashboard page"],
        "/": ["go to home", "home page", "main page", "homepage", "take me home", "home"],
        "/bookings/": ["go to booking", "show my booking", "my booking", "booking page"],
        "/Chat/": ["show my chat", "go to chat", "my chat", "chat page"],
    }
    
    for path, patterns in nav_patterns.items():
        for pattern in patterns:
            if pattern in lowered:
                return path
    
    return None


def _generate_service_error_reply():
    """Return a friendly message when AI service fails."""
    return "AI not available at the moment thank you"


def _safe_error_message(error):
    text = str(error)
    for secret_name in ("GEMINI_API_KEY", "FLUTTERWAVE_SECRET_KEY", "IMAGEKIT_PRIVATE_KEY", "IMAGEKIT_PUBLIC_KEY"):
        secret = os.getenv(secret_name)
        if secret:
            text = text.replace(secret, "***")
    return text


def _create_admin_alert(error, conversation, state):
    """Create an admin alert for AI service failures."""
    try:
        error_type = type(error).__name__
        error_message = _safe_error_message(error)
        
        # Determine alert type based on error
        if "timeout" in error_message.lower() or "timed out" in error_message.lower():
            alert_type = "api_timeout"
            title = "Gemini API Timeout"
        else:
            alert_type = "ai_error"
            title = f"AI Service Error: {error_type}"
        
        # Create the admin alert
        AdminAlert.objects.create(
            alert_type=alert_type,
            title=title,
            message=f"Error occurred while generating AI response for conversation {conversation.id}",
            error_details={
                "error_type": error_type,
                "error_message": error_message,
                "conversation_id": str(conversation.id),
                "user_id": conversation.user.id if conversation.user else None,
                "state": state,
            }
        )
        logger.warning(f"Created admin alert for {alert_type}: {title}")
    except Exception as alert_error:
        logger.error(f"Failed to create admin alert: {alert_error}", exc_info=True)


def assistant_suggestions():
    return [
        "I need a tutor in PH for my SS2 daughter.",
        "My child is 12 and needs help with Mathematics on weekends.",
        "I want to learn Python from beginner level.",
        "I need help with CSS and frontend web design.",
        "Can you help me understand my Physics assignment?",
        *suggested_prompts(),
    ]


