import json
import logging
import os

from openai import OpenAI

from .models import AIMessage
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

    request.session["ai_conversation_id"] = conversation.id
    return conversation


def reset_conversation(request):
    from .models import AIConversation

    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        conversation = AIConversation.objects.create(user=request.user, session_key=request.session.session_key)
    else:
        conversation = AIConversation.objects.create(session_key=request.session.session_key)

    request.session["ai_conversation_id"] = conversation.id
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
        handle_user_message(conversation, initial_prompt)
    return conversation


def handle_user_message(conversation, user_text):
    user_text = (user_text or "").strip()
    if not user_text:
        return None

    AIMessage.objects.create(conversation=conversation, role=AIMessage.ROLE_USER, content=user_text)

    state = _merge_state(conversation)
    tutors = _recommend_tutors(state)
    assistant_text = _generate_assistant_reply(conversation, state, tutors)

    assistant_message = AIMessage.objects.create(
        conversation=conversation,
        role=AIMessage.ROLE_ASSISTANT,
        content=assistant_text,
        metadata={"tutors": tutors[:3], "state": state},
    )
    conversation.state = state
    conversation.save(update_fields=["state", "updated_at"])
    return assistant_message


def _merge_state(conversation):
    previous_state = conversation.state or {}
    user_text = "\n".join(
        conversation.messages.filter(role=AIMessage.ROLE_USER).values_list("content", flat=True)
    )
    latest_intent = extract_search_intent(user_text)

    state = {
        "query_text": user_text,
        "subject": latest_intent.get("subject") or previous_state.get("subject", ""),
        "level": latest_intent.get("level") or previous_state.get("level", ""),
        "location": latest_intent.get("location") or previous_state.get("location", ""),
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

    if not os.getenv("OPENAI_API_KEY"):
        return "OpenAI API Key is missing. Please configure it in your .env file."
    try:
        return _generate_openai_reply(conversation, state, tutors)
    except Exception as e:
        logger.error("OpenAI assistant response failed.", exc_info=True)
        return f"Error contacting OpenAI API: {str(e)}. Please check your API key configuration."


def _generate_openai_reply(conversation, state, tutors):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    messages = _conversation_input(conversation, state, tutors)

    if hasattr(client, "responses"):
        response = client.responses.create(
            model=model,
            instructions=ASSISTANT_INSTRUCTIONS,
            input=messages,
        )
        return getattr(response, "output_text", "") or _generate_fallback_reply(state, tutors)

    response = client.chat.completions.create(
        model=model,
        temperature=0.4,
        messages=[{"role": "system", "content": ASSISTANT_INSTRUCTIONS}, *messages],
    )
    return response.choices[0].message.content


def _conversation_input(conversation, state, tutors):
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in conversation.messages.order_by("-created_at")[:12]
    ]
    history.reverse()
    context = {
        "role": "developer",
        "content": (
            "Current extracted student need:\n"
            f"{json.dumps(state, ensure_ascii=True)}\n\n"
            "Available tutor matches from our database:\n"
            f"{json.dumps(tutors[:5], ensure_ascii=True)}\n\n"
            "If required details are missing, ask the next best question. "
            "If tutor matches exist, recommend them by name and why they fit. "
            "If the student asks for assignment or course help, teach briefly and suggest a learning path."
        ),
    }
    return [context, *history]


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


def assistant_suggestions():
    return [
        "I need a tutor in PH for my SS2 daughter.",
        "My child is 12 and needs help with Mathematics on weekends.",
        "I want to learn HTML from beginner level.",
        "Can you help me understand my Physics assignment?",
        *suggested_prompts(),
    ]


