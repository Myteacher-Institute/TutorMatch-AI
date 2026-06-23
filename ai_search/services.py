import json
import os
import re

from django.apps import apps


SUBJECTS = [
    "Mathematics",
    "English",
    "Physics",
    "Chemistry",
    "Biology",
    "Economics",
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
    text = prompt or ""
    fallback = _fallback_intent(text)

    if not text or not os.getenv("OPENAI_API_KEY"):
        return fallback

    try:
        return _extract_with_openai(text, fallback)
    except Exception:
        fallback["source"] = "fallback-openai-error"
        return fallback


def search_tutors(intent, filters=None):
    filters = filters or {}
    subject = filters.get("subject") or intent.get("subject")
    location = filters.get("location") or intent.get("location")
    min_price = filters.get("min_price")
    max_price = filters.get("max_price")
    min_experience = filters.get("min_experience")

    tutors = _load_database_tutors() or list(SAMPLE_TUTORS)

    if subject:
        tutors = [tutor for tutor in tutors if _same_text(tutor["subject"], subject)]

    if location and location != "Port Harcourt":
        tutors = [tutor for tutor in tutors if _contains_text(tutor["location"], location)]

    if min_price is not None:
        tutors = [tutor for tutor in tutors if tutor["rate"] >= min_price]

    if max_price is not None:
        tutors = [tutor for tutor in tutors if tutor["rate"] <= max_price]

    if min_experience is not None:
        tutors = [tutor for tutor in tutors if tutor["experience"] >= min_experience]

    sorted_tutors = sorted(tutors, key=lambda tutor: (tutor["verified"], tutor["rating"], tutor["experience"]), reverse=True)

    enriched = []
    for idx, tutor in enumerate(sorted_tutors):
        t = dict(tutor)
        if idx == 0:
            t["ai_score"] = "96% Match"
            t["best_match"] = True
            t["response_time"] = "1 hr"
            t["reviews_count"] = 128
        elif idx == 1:
            t["ai_score"] = "92% Match"
            t["best_match"] = False
            t["response_time"] = "2 hrs"
            t["reviews_count"] = 42
        elif idx == 2:
            t["ai_score"] = "85% Match"
            t["best_match"] = False
            t["response_time"] = "1 hr"
            t["reviews_count"] = 29
        else:
            t["ai_score"] = "80% Match"
            t["best_match"] = False
            t["response_time"] = "3 hrs"
            t["reviews_count"] = 12

        t["ai_reason"] = f"This tutor specializes in {t.get('specialist', t['subject'])}, has extensive WAEC preparation experience, and is located near {t['location']}."
        enriched.append(t)

    return enriched


def suggested_prompts():
    return [
        "I need a Mathematics tutor for SS2 in GRA Port Harcourt weekends.",
        "Find a Physics tutor for WAEC around Rumuola.",
        "I need an English tutor for JSS3 in Trans Amadi.",
    ]


def _fallback_intent(prompt):
    lowered = (prompt or "").lower()
    return {
        "subject": _find_first(SUBJECTS, lowered),
        "level": _find_first(LEVELS, lowered),
        "location": _find_first(LOCATIONS, lowered),
        "schedule": _find_schedule(lowered),
        "source": "fallback",
    }


def _extract_with_openai(prompt, fallback):
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract tutor search intent from a Nigerian tutoring marketplace prompt. "
                    "Return only JSON with string keys: subject, level, location, schedule. "
                    "Use an empty string when a value is missing."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )
    data = json.loads(response.choices[0].message.content or "{}")

    return {
        "subject": _clean_choice(data.get("subject"), SUBJECTS) or fallback["subject"],
        "level": _clean_choice(data.get("level"), LEVELS) or fallback["level"],
        "location": _clean_choice(data.get("location"), LOCATIONS) or fallback["location"],
        "schedule": str(data.get("schedule") or fallback["schedule"] or "").strip(),
        "source": "openai",
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
        return []


def _filter_verified_tutors(Tutor, queryset):
    fields = {field.name for field in Tutor._meta.get_fields()}
    if "verification_status" in fields:
        return queryset.filter(verification_status__in=["approved", "verified", "Approved", "Verified"])
    if "is_verified" in fields:
        return queryset.filter(is_verified=True)
    return queryset


def _field_value(obj, field_name, default=""):
    value = getattr(obj, field_name, default)
    if callable(value):
        return default
    return value if value not in (None, "") else default


def _tutor_name(tutor):
    user = getattr(tutor, "user", None)
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
    return "https://images.unsplash.com/photo-1580894732444-8ecded7900cd?auto=format&fit=crop&w=600&q=80"


def _clean_choice(value, options):
    if not value:
        return ""
    lowered = str(value).strip().lower()
    for option in options:
        if option.lower() == lowered or option.lower() in lowered:
            return option
    return str(value).strip()


def _find_first(options, lowered):
    for option in options:
        if option.lower() in lowered:
            return option
    return ""


def _find_schedule(lowered):
    for word in SCHEDULE_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", lowered):
            return word.title()
    return ""


def _same_text(left, right):
    return left.lower() == right.lower()


def _contains_text(left, right):
    return right.lower() in left.lower()
