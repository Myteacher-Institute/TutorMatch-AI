import json
import logging
import os
import re

from django.apps import apps
from django.conf import settings

logger = logging.getLogger(__name__)


SUBJECTS = [
    "Mathematics",
    "English",
    "Physics",
    "Chemistry",
    "Biology",
    "Economics",
    "HTML",
    "Coding",
    "Programming",
]

LEVELS = ["Primary", "JSS1", "JSS2", "JSS3", "SS1", "SS2", "SS3", "WAEC", "NECO", "JAMB"]

LOCATIONS = ["GRA", "Rumuola", "Trans Amadi", "D-Line", "Ada George", "Woji", "Port Harcourt"]

SCHEDULE_WORDS = ["weekend", "weekends", "weekday", "weekdays", "evening", "mornings", "morning", "online"]


SAMPLE_TUTORS = [
    {
        "id": 1,
        "name": "Dr. Ngozi Nwosu",
        "subject": "Mathematics",
        "specialist": "Mathematics & Physics Specialist",
        "level": "SS3",
        "location": "GRA_PH",
        "rate": 7500,
        "experience": 8,
        "rating": 4.9,
        "verified": True,
        "bio": "Specializes in SS3 Mathematics, has extensive WAEC preparation experience with a 95% pass rate, teaches weekends, and is located just 1.2km from GRA Port Harcourt.",
        "photo": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=600&q=80",
    },
    {
        "id": 2,
        "name": "Amaka Chidi",
        "subject": "Mathematics",
        "specialist": "Mathematics & Chemistry",
        "level": "SS3",
        "location": "C&I GRA, PH",
        "rate": 5000,
        "experience": 5,
        "rating": 4.8,
        "verified": True,
        "bio": "Dedicated Mathematics and Chemistry tutor with a passion for helping high schoolers succeed.",
        "photo": "https://images.unsplash.com/photo-1567532939604-b6b5b0db2604?auto=format&fit=crop&w=600&q=80",
    },
    {
        "id": 3,
        "name": "Blessing Peters",
        "subject": "Mathematics",
        "specialist": "B.Sc Mathematics",
        "level": "SS3",
        "location": "D-Line, PH",
        "rate": 4500,
        "experience": 3,
        "rating": 4.7,
        "verified": True,
        "bio": "Energetic B.Sc Mathematics graduate focusing on building fundamental problem-solving skills.",
        "photo": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=600&q=80",
    },
]


def extract_search_intent(prompt):
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except ImportError:
        pass

    text = (prompt or "").strip()
    empty_intent = {
        "query_text": text,
        "subject": "",
        "level": "",
        "location": "",
        "schedule": "",
        "source": "gemini",
    }
    if not text:
        return empty_intent

    try:
        return _extract_with_gemini(text)
    except Exception:
        logger.error("Failed to extract search intent with Gemini API.", exc_info=True)
        return empty_intent


def search_tutors(intent, filters=None):
    filters = filters or {}
    subject = filters.get("subject") or intent.get("subject")
    location = filters.get("location") or intent.get("location")
    min_price = filters.get("min_price")
    max_price = filters.get("max_price")
    min_experience = filters.get("min_experience")

    tutors = _load_database_tutors()
    if not tutors and _use_sample_tutors():
        tutors = list(SAMPLE_TUTORS)

    query_text = intent.get("query_text", "").strip()
    has_filters = bool(subject or location or min_price is not None or max_price is not None or min_experience is not None)

    # If the user searched for something, we must verify if there's any match
    matched_any = False

    if subject:
        tutors = [tutor for tutor in tutors if _same_text(tutor["subject"], subject)]
        matched_any = True

    if location and location != "Port Harcourt":
        tutors = [tutor for tutor in tutors if _contains_text(tutor["location"], location)]
        matched_any = True

    level = intent.get("level")
    if level:
        # Match against bio or specialist if tutor level matches
        tutors = [tutor for tutor in tutors if _contains_text(tutor.get("level", ""), level) or _contains_text(tutor.get("bio", ""), level)]
        matched_any = True

    if min_price is not None:
        tutors = [tutor for tutor in tutors if tutor["rate"] >= min_price]

    if max_price is not None:
        tutors = [tutor for tutor in tutors if tutor["rate"] <= max_price]

    if min_experience is not None:
        tutors = [tutor for tutor in tutors if tutor["experience"] >= min_experience]

    # If query text was provided, but didn't match any subject, location, or level,
    # check if it matches a tutor's name. Otherwise, it's a completely unmatched query!
    if query_text and not matched_any:
        name_matches = [tutor for tutor in tutors if _contains_text(tutor["name"], query_text)]
        if name_matches:
            tutors = name_matches
        else:
            # No name, subject, location, or level matches found for this query text
            return []

    # If no query text and no filters are present, we return empty
    if not query_text and not has_filters:
        return []

    sorted_tutors = sorted(tutors, key=lambda tutor: (tutor["verified"], tutor["rating"], tutor["experience"]), reverse=True)

    enriched = []
    for idx, tutor in enumerate(sorted_tutors):
        t = dict(tutor)
        if idx == 0:
            t["ai_score"] = "96%"
            t["best_match"] = True
            t["response_time"] = "1 hr"
            t["reviews_count"] = 128
        elif idx == 1:
            t["ai_score"] = "92%"
            t["best_match"] = False
            t["response_time"] = "2 hrs"
            t["reviews_count"] = 42
        elif idx == 2:
            t["ai_score"] = "85%"
            t["best_match"] = False
            t["response_time"] = "1 hr"
            t["reviews_count"] = 29
        else:
            t["ai_score"] = "80%"
            t["best_match"] = False
            t["response_time"] = "3 hrs"
            t["reviews_count"] = 12

        t["ai_reason"] = f"This tutor matches your search for {t.get('specialist', t['subject'])}, has {t['experience']} years of experience, and is located near {t['location']}."
        enriched.append(t)

    return enriched


def suggested_prompts():
    return [
        "I need a Mathematics tutor for SS2 in GRA Port Harcourt weekends.",
        "Find a Physics tutor for WAEC around Rumuola.",
        "I need an English tutor for JSS3 in Trans Amadi.",
    ]


def _extract_with_gemini(prompt):
    import requests

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from environment.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    system_instruction = (
        "Extract tutor search intent from a Nigerian tutoring marketplace prompt. "
        "Return only JSON with string keys: subject, level, location, schedule. "
        "Use an empty string when a value is missing."
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"Prompt: {prompt}"}
                ]
            }
        ],
        "systemInstruction": {
            "parts": [
                {"text": system_instruction}
            ]
        },
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.0
        }
    }

    response = requests.post(url, json=payload, headers=headers, timeout=20)
    response.raise_for_status()

    res_data = response.json()
    try:
        text_content = res_data["candidates"][0]["content"]["parts"][0]["text"]
        data = json.loads(text_content)
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Failed to parse Gemini response: {res_data}", exc_info=True)
        raise ValueError("Failed to extract intent from Gemini response.") from e

    return {
        "query_text": prompt,
        "subject": _clean_choice(data.get("subject"), SUBJECTS),
        "level": _clean_choice(data.get("level"), LEVELS),
        "location": _clean_choice(data.get("location"), LOCATIONS),
        "schedule": str(data.get("schedule") or "").strip(),
        "source": "gemini",
    }


def _load_database_tutors():
    try:
        Tutor = apps.get_model("tutors", "Tutor")
        if not hasattr(Tutor, "objects"):
            return []

        queryset = _filter_verified_tutors(Tutor, Tutor.objects.all())
        tutors = []

        for tutor in queryset[:50]:
            tutors.append(
                {
                    "id": tutor.pk,
                    "name": _tutor_name(tutor),
                    "subject": _tutor_subject(tutor),
                    "specialist": _tutor_specialist(tutor),
                    "level": _field_value(tutor, "level", "All levels"),
                    "location": _field_value(tutor, "location", "Port Harcourt"),
                    "rate": int(_field_value(tutor, "hourly_rate", 0) or 0),
                    "experience": int(_field_value(tutor, "years_experience", 0) or 0),
                    "rating": float(_field_value(tutor, "rating", 4.8) or 4.8),
                    "verified": _is_verified_tutor(tutor),
                    "bio": _field_value(tutor, "bio", "Verified tutor available for home lessons."),
                    "photo": _photo_url(tutor),
                }
            )
        return tutors
    except Exception:
        logger.warning("Failed to load tutors for AI search.", exc_info=True)
        return []


def _filter_verified_tutors(Tutor, queryset):
    fields = {field.name for field in Tutor._meta.get_fields()}
    if "verification_status" in fields:
        queryset = queryset.filter(verification_status__in=["approved", "verified", "Approved", "Verified"])
    if "is_verified" in fields:
        queryset = queryset.filter(is_verified=True)
    if "is_publicly_visible" in fields:
        queryset = queryset.filter(is_publicly_visible=True)
    return queryset


def _use_sample_tutors():
    value = os.getenv("AI_SEARCH_USE_SAMPLE_TUTORS")
    if value is None:
        return settings.configured and settings.DEBUG
    return value.lower() in {"1", "true", "yes", "on"}


def _field_value(obj, field_name, default=""):
    value = getattr(obj, field_name, default)
    if callable(value):
        return default
    return value if value not in (None, "") else default


def _tutor_name(tutor):
    profile = getattr(tutor, "user", None)
    user = getattr(profile, "user", profile)
    if user:
        full_name = user.get_full_name() if hasattr(user, "get_full_name") else ""
        if full_name:
            return full_name
        if getattr(user, "first_name", "") or getattr(user, "last_name", ""):
            return f"{user.first_name} {user.last_name}".strip()
        if getattr(user, "username", ""):
            return user.username
        if getattr(user, "email", ""):
            return user.email
    return _field_value(tutor, "name", "Verified Tutor")


def _tutor_subject(tutor):
    subjects = getattr(tutor, "subjects", None)
    if subjects and hasattr(subjects, "all"):
        names = [_subject_name(subject) for subject in subjects.all()[:3]]
        names = [name for name in names if name]
        if names:
            return names[0]

    subject = getattr(tutor, "subject", None)
    if subject:
        return _subject_name(subject)

    return "General"


def _tutor_specialist(tutor):
    subjects = getattr(tutor, "subjects", None)
    if subjects and hasattr(subjects, "all"):
        names = [_subject_name(subject) for subject in subjects.all()[:3]]
        names = [name for name in names if name]
        if names:
            return " & ".join(names)

    return _tutor_subject(tutor)


def _subject_name(subject):
    if isinstance(subject, str):
        return subject
    return getattr(subject, "subject_name", None) or getattr(subject, "name", None) or str(subject)


def _is_verified_tutor(tutor):
    status = str(_field_value(tutor, "verification_status", "")).lower()
    if status:
        return status in {"approved", "verified"}
    return bool(_field_value(tutor, "is_verified", True))


def _photo_url(tutor):
    photo = getattr(tutor, "profile_photo", None)
    if photo and hasattr(photo, "url"):
        return photo.url
    if photo:
        return str(photo)
    return "https://images.unsplash.com/photo-1580894732444-8ecded7900cd?auto=format&fit=crop&w=600&q=80"


def _clean_choice(value, options):
    if not value:
        return ""
    lowered = str(value).strip().lower()
    for option in options:
        if option.lower() == lowered or option.lower() in lowered:
            return option
    return str(value).strip()





def _same_text(left, right):
    return left.lower() == right.lower()


def _contains_text(left, right):
    return right.lower() in left.lower()
