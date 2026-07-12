import json
import logging
import os
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
- Collect: subject/course, student age or class level, location, learning goal, schedule, budget, and whether online or home tutoring is preferred.
- When tutor matches are provided, recommend the best options and explain why they fit the conversation.
- If there are no tutor matches yet, keep helping: refine the need, suggest nearby/broader options, and propose next learning steps.
- Help with assignments by guiding and explaining. Do not simply do all assessed work for the student.
- Suggest courses or learning paths when the student wants to learn something like HTML, coding, WAEC prep, JAMB prep, or school subjects.
- Be concise, friendly, and practical. Use Nigerian context where helpful.
"""


REQUIRED_MATCH_FIELDS = ["subject", "level", "location"]


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
    return conversation


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

        state = _merge_state(locked_conv)
        tutors = _recommend_tutors(state)
        assistant_text = _generate_assistant_reply(locked_conv, state, tutors)

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
    user_text = "\n".join(
        conversation.messages.filter(role=AIMessage.ROLE_USER).values_list("content", flat=True)
    )
    latest_intent = extract_search_intent(user_text)

    # Try to get user's profile location if they're authenticated
    location = latest_intent.get("location") or previous_state.get("location", "")
    if not location and conversation.user:
        try:
            tutor_profile = conversation.user.tutor_profile
            if tutor_profile and tutor_profile.location:
                location = tutor_profile.location
        except:
            pass

    state = {
        "query_text": user_text,
        "subject": latest_intent.get("subject") or previous_state.get("subject", ""),
        "level": latest_intent.get("level") or previous_state.get("level", ""),
        "location": location,
        "schedule": latest_intent.get("schedule") or previous_state.get("schedule", ""),
        "source": latest_intent.get("source", "fallback"),
    }
    state["missing_fields"] = [field for field in REQUIRED_MATCH_FIELDS if not state.get(field)]
    state["ready_for_tutor_match"] = not state["missing_fields"]
    state["learning_mode"] = _detect_learning_mode(user_text)
    return state


def _recommend_tutors(state):
    if not state.get("ready_for_tutor_match"):
        return []
    return search_tutors(state, {})[:5]


def _generate_assistant_reply(conversation, state, tutors):
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except ImportError:
        pass

    if not os.getenv("GEMINI_API_KEY"):
        return _generate_fallback_reply(state, tutors)
    try:
        return _generate_gemini_reply(conversation, state, tutors)
    except Exception as e:
        logger.error("Gemini assistant response failed.", exc_info=True)
        # Create admin alert for the error
        _create_admin_alert(e, conversation, state)
        # Return a friendly message to the user
        return _generate_service_error_reply()


def _generate_gemini_reply(conversation, state, tutors):
    import requests

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from environment.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    system_text = (
        f"{ASSISTANT_INSTRUCTIONS}\n\n"
        "Current extracted student need:\n"
        f"{json.dumps(state, ensure_ascii=True)}\n\n"
        "Available tutor matches from our database:\n"
        f"{json.dumps(tutors[:5], ensure_ascii=True)}\n\n"
        "If required details are missing, ask the next best question. "
        "If tutor matches exist, recommend them by name and why they fit. "
        "If the student asks for assignment or course help, teach briefly and suggest a learning path."
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

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        res_data = response.json()
        try:
            reply_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return reply_text
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Failed to parse Gemini response: {res_data}", exc_info=True)
            raise ValueError("Failed to get response from Gemini API.") from e
    except requests.exceptions.Timeout as e:
        logger.error(f"Gemini API timeout after 30 seconds", exc_info=True)
        raise TimeoutError("Gemini API did not respond within 30 seconds") from e
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Gemini API connection error: {e}", exc_info=True)
        raise ConnectionError("Failed to connect to Gemini API service") from e


def _generate_fallback_reply(state, tutors):
    if tutors:
        lines = ["I found tutor options that fit what you told me:"]
        for tutor in tutors[:3]:
            lines.append(
                f"- {tutor['name']}: {tutor.get('specialist', tutor['subject'])}, "
                f"{tutor['experience']} years experience, around {tutor['location']}, "
                f"NGN {tutor['rate']}/hr."
            )
        lines.append("Would you like the cheapest option, the most experienced option, or the best overall match?")
        return "\n".join(lines)

    missing = state.get("missing_fields", [])
    if "subject" in missing:
        return "Sure. What subject or skill does the student want help with? For example Mathematics, English, HTML, WAEC, or JAMB."
    if "level" in missing:
        return "Got it. How old is the student, or what class/level are they in?"
    if "location" in missing:
        return "Great. What location should I search around? You can say Port Harcourt, GRA, Rumuola, Woji, or online."

    if state.get("learning_mode") == "course":
        return _course_suggestion_reply(state)

    return (
        "I understand. I do not see a strong tutor match yet, but I can broaden the search by nearby locations, "
        "online lessons, schedule, or budget. Which one should I adjust first?"
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


def _generate_service_error_reply():
    """Return a friendly message when AI service fails."""
    return (
        "I'm experiencing a temporary issue connecting to the AI service. "
        "Please try again in a moment. If the problem continues, our team has been notified. "
        "In the meantime, I can still help you search for tutors if you tell me the subject, level, and location."
    )


def _create_admin_alert(error, conversation, state):
    """Create an admin alert for AI service failures."""
    try:
        error_type = type(error).__name__
        error_message = str(error)
        
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
        "I want to learn HTML from beginner level.",
        "Can you help me understand my Physics assignment?",
        *suggested_prompts(),
    ]


