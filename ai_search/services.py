import json
import logging
import os
import re
import time

from django.apps import apps
from django.conf import settings

logger = logging.getLogger(__name__)


def _safe_error_message(error):
    text = str(error)
    secret = os.getenv("GEMINI_API_KEY")
    if secret:
        text = text.replace(secret, "***")
    return text


DEFAULT_SUBJECTS = [
    "Mathematics",
    "English",
    "Physics",
    "Chemistry",
    "Biology",
    "Economics",
    "Django",
    "FastAPI",
    "Flask",
    "HTML",
    "CSS",
    "JavaScript",
    "Python",
    "C++",
    "Coding",
    "Programming",
]

LEVELS = ["Primary", "JSS1", "JSS2", "JSS3", "SS1", "SS2", "SS3", "WAEC", "NECO", "JAMB"]

DEFAULT_LOCATIONS = ["GRA", "Rumuola", "Trans Amadi", "D-Line", "Ada George", "Woji", "Port Harcourt"]

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
        "mode": "",
        "wants_more": False,
        "source": "gemini",
    }
    if not text:
        return empty_intent

    rule_intent = _extract_with_rules(text, empty_intent)
    try:
        gemini_intent = _extract_with_gemini(text)
        return {
            "query_text": text,
            "subject": rule_intent.get("subject") or gemini_intent.get("subject", ""),
            "level": rule_intent.get("level") or gemini_intent.get("level", ""),
            "location": rule_intent.get("location") or gemini_intent.get("location", ""),
            "schedule": gemini_intent.get("schedule", "") or rule_intent.get("schedule", ""),
            "mode": rule_intent.get("mode") or gemini_intent.get("mode", ""),
            "wants_more": rule_intent.get("wants_more", False) or gemini_intent.get("wants_more", False),
            "source": "rules+gemini" if rule_intent.get("subject") or rule_intent.get("location") else gemini_intent.get("source", "gemini"),
        }
    except Exception:
        logger.warning("Failed to extract search intent with Gemini API.")
        return rule_intent


def _extract_with_rules(text, base_intent=None):
    intent = dict(base_intent or {})
    normalized = _normalize_text(text)

    subject_patterns = [
        ("Django", ["django"]),
        ("FastAPI", ["fastapi", "fast api"]),
        ("Flask", ["flask"]),
        ("Python Backend", ["python backend", "backend python"]),
        ("Python", ["python", "py"]),
        ("C++", ["c++", "cpp"]),
        ("CSS", ["css"]),
        ("HTML", ["html"]),
        ("JavaScript", ["javascript", "js"]),
        ("Web Development", ["web development", "frontend", "website"]),
        ("Coding", ["coding", "programming"]),
        ("Mathematics", ["mathematics", "maths", "math"]),
        ("English", ["english"]),
        ("Physics", ["physics"]),
        ("Chemistry", ["chemistry"]),
        ("Biology", ["biology"]),
        ("Economics", ["economics"]),
        ("WAEC", ["waec"]),
        ("JAMB", ["jamb"]),
    ]
    subject_match = _latest_pattern_match(normalized, subject_patterns)
    if subject_match:
        intent["subject"] = subject_match

    level_patterns = [
        ("Beginner", ["0 knowledge", "zero knowledge", "complete beginner", "beginner", "no programming"]),
        ("Intermediate", ["intermediate", "some experience"]),
        ("Advanced", ["advanced"]),
        *[(level, [level.lower()]) for level in LEVELS],
    ]
    level_match = _latest_pattern_match(normalized, level_patterns)
    if level_match:
        intent["level"] = level_match

    location_patterns = [
        ("Port Harcourt", ["port harcourt", "ph"]),
        ("GRA", ["gra"]),
        ("Rumuola", ["rumuola"]),
        ("Trans Amadi", ["trans amadi"]),
        ("D-Line", ["d line", "d-line"]),
        ("Ada George", ["ada george"]),
        ("Woji", ["woji"]),
        ("Online", ["online", "remote"]),
    ]
    location_match = _latest_pattern_match(normalized, location_patterns)
    if location_match:
        intent["location"] = location_match

    mode_patterns = [
        ("Online", ["online", "remote", "virtual", "zoom"]),
        ("Home", ["home", "physical", "in-person", "in person"]),
    ]
    mode_match = _latest_pattern_match(normalized, mode_patterns)
    if mode_match:
        intent["mode"] = mode_match

    intent["wants_more"] = any(word in normalized for word in ["more", "other", "another", "different", "next"])

    intent["source"] = "rules"
    return intent


def search_tutors(intent, filters=None):
    filters = filters or {}
    subject = filters.get("subject") or intent.get("subject")
    location = filters.get("location") or intent.get("location")
    mode = intent.get("mode", "").strip()
    min_price = filters.get("min_price")
    max_price = filters.get("max_price")
    min_experience = filters.get("min_experience")

    tutors = _load_database_tutors()
    if not tutors and _use_sample_tutors():
        tutors = list(SAMPLE_TUTORS)

    query_text = intent.get("query_text", "").strip()
    has_filters = bool(subject or location or mode or min_price is not None or max_price is not None or min_experience is not None)

    matched_any = False

    if subject:
        filtered_tutors = []
        for tutor in tutors:
            if _matches_subject(tutor, subject):
                t_copy = dict(tutor)
                # Keep matching course offers for this subject
                matching_offers = [
                    o for o in tutor.get("course_offers", [])
                    if _normalize_text(subject) in _normalize_text(f"{o.get('title')} {o.get('subject')}")
                    or any(_normalize_text(term) in _normalize_text(f"{o.get('title')} {o.get('subject')}") for term in _skill_terms(subject))
                ]
                t_copy["matching_course_offers"] = matching_offers if matching_offers else tutor.get("course_offers", [])
                filtered_tutors.append(t_copy)
        tutors = filtered_tutors
        matched_any = True

    if mode:
        mode_lower = mode.lower()
        filtered_by_mode = []
        for tutor in tutors:
            offers = tutor.get("matching_course_offers") or tutor.get("course_offers", [])
            if "online" in mode_lower or "remote" in mode_lower:
                online_offers = [o for o in offers if o.get("mode_code") == "online"]
                if online_offers:
                    t_copy = dict(tutor)
                    t_copy["matching_course_offers"] = online_offers
                    filtered_by_mode.append(t_copy)
                elif "online" in tutor.get("bio", "").lower() or not offers:
                    filtered_by_mode.append(tutor)
            elif "home" in mode_lower or "physical" in mode_lower:
                home_offers = [o for o in offers if o.get("mode_code") in ["home", "office"]]
                if home_offers:
                    t_copy = dict(tutor)
                    t_copy["matching_course_offers"] = home_offers
                    filtered_by_mode.append(t_copy)
                elif "home" in tutor.get("bio", "").lower() or not offers:
                    filtered_by_mode.append(tutor)
        if filtered_by_mode:
            tutors = filtered_by_mode
        matched_any = True

    # If location specified and not online-only mode
    if location and not ("online" in mode.lower()):
        location_matches = [tutor for tutor in tutors if _matches_location(tutor["location"], location)]
        if location_matches:
            tutors = location_matches
            matched_any = True

    level = intent.get("level")
    if level and level in LEVELS:
        tutors = [tutor for tutor in tutors if _contains_text(tutor.get("level", ""), level) or _contains_text(tutor.get("bio", ""), level)]
        matched_any = True

    if min_price is not None:
        tutors = [tutor for tutor in tutors if tutor["rate"] >= min_price]

    if max_price is not None:
        tutors = [tutor for tutor in tutors if tutor["rate"] <= max_price]

    if min_experience is not None:
        tutors = [tutor for tutor in tutors if tutor["experience"] >= min_experience]

    if query_text and not matched_any:
        name_matches = [tutor for tutor in tutors if _matches_query(tutor, query_text)]
        if name_matches:
            tutors = name_matches
        else:
            return []

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
    configured_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from environment.")

    headers = {"Content-Type": "application/json"}

    system_instruction = (
        "Extract tutor search intent from a Nigerian tutoring marketplace prompt. "
        "The subject can be an academic subject, exam, course, or tech skill such as Python, C++, CSS, HTML, or coding. "
        "Return only JSON with string keys: subject, level, location, schedule, mode (e.g. 'Online' or 'Home'), and a boolean key: wants_more (true if user asks for more or other options). "
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
                    timeout=20,
                )
                if response.status_code in {429, 500, 502, 503, 504} and attempt == 0:
                    time.sleep(1)
                    continue
                response.raise_for_status()

                res_data = response.json()
                try:
                    text_content = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    data = json.loads(text_content)
                    break
                except (KeyError, IndexError, ValueError) as e:
                    logger.error(f"Failed to parse Gemini response: {res_data}", exc_info=True)
                    raise ValueError("Failed to extract intent from Gemini response.") from e
            else:
                continue
            break
        except requests.exceptions.RequestException as e:
            logger.warning("Gemini intent extraction failed for model %s: %s", model, _safe_error_message(e))
            last_error = e
    else:
        raise last_error or ConnectionError("Failed to extract intent from Gemini API.")

    return {
        "query_text": prompt,
        "subject": _clean_choice(data.get("subject"), _known_subjects()),
        "level": _clean_choice(data.get("level"), LEVELS),
        "location": _clean_choice(data.get("location"), _known_locations()),
        "schedule": str(data.get("schedule") or "").strip(),
        "mode": str(data.get("mode") or "").strip(),
        "wants_more": bool(data.get("wants_more", False)),
        "source": "gemini",
    }


def _load_database_tutors():
    try:
        Tutor = apps.get_model("tutors", "Tutor")
        CourseOffer = apps.get_model("tutors", "CourseOffer")
        if not hasattr(Tutor, "objects"):
            return []

        queryset = _filter_verified_tutors(Tutor, Tutor.objects.all().prefetch_related("course_offers", "subjects"))
        tutors = []

        for tutor in queryset[:50]:
            offers = []
            if hasattr(tutor, "course_offers"):
                for offer in tutor.course_offers.filter(is_active=True):
                    cover_img = ""
                    if hasattr(offer, "cover_image_url") and offer.cover_image_url:
                        cover_img = offer.cover_image_url
                    elif hasattr(offer, "cover_image_file") and offer.cover_image_file:
                        try:
                            cover_img = offer.cover_image_file.url
                        except Exception:
                            cover_img = ""

                    offers.append({
                        "id": offer.pk,
                        "title": offer.title,
                        "subject": offer.subject.subject_name if getattr(offer, "subject", None) else "",
                        "delivery_mode": offer.get_delivery_mode_display() if hasattr(offer, "get_delivery_mode_display") else "Class",
                        "mode_code": getattr(offer, "delivery_mode", "online"),
                        "total_price": float(getattr(offer, "total_course_price", 0)),
                        "price_display": f"{getattr(offer, 'currency_symbol', '₦')}{getattr(offer, 'total_course_price', 0):,.0f}",
                        "daily_rate_display": f"{getattr(offer, 'currency_symbol', '₦')}{getattr(offer, 'daily_rate', 0):,.0f}/day",
                        "duration_weeks": getattr(offer, "duration_weeks", 4),
                        "days_per_week": getattr(offer, "days_per_week", 2),
                        "duration_display": f"{getattr(offer, 'duration_weeks', 4)} wk(s) ({getattr(offer, 'days_per_week', 2)} days/wk)",
                        "cover_image": cover_img,
                    })

            subjects_list = _tutor_subjects(tutor)
            for o in offers:
                if o["subject"] and o["subject"] not in subjects_list:
                    subjects_list.append(o["subject"])
                if o["title"] and o["title"] not in subjects_list:
                    subjects_list.append(o["title"])

            tutors.append(
                {
                    "id": tutor.pk,
                    "name": _tutor_name(tutor),
                    "subject": _tutor_subject(tutor),
                    "subjects": subjects_list,
                    "specialist": _tutor_specialist(tutor),
                    "level": _field_value(tutor, "level", "All levels"),
                    "location": _field_value(tutor, "location", "Port Harcourt"),
                    "rate": int(offers[0]["total_price"]) if offers else int(_field_value(tutor, "rate_amount", 0) or 0),
                    "rate_period": "course",
                    "experience": int(_field_value(tutor, "years_experience", 0) or 0),
                    "rating": float(_field_value(tutor, "rating", 4.8) or 4.8),
                    "verified": _is_verified_tutor(tutor),
                    "bio": _field_value(tutor, "bio", "Verified tutor available for home & online lessons."),
                    "photo": _photo_url(tutor),
                    "course_offers": offers,
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
    names = _tutor_subjects(tutor)
    if names:
        return names[0]

    subject = getattr(tutor, "subject", None)
    if subject:
        return _subject_name(subject)

    return "General"


def _tutor_subjects(tutor):
    subjects = getattr(tutor, "subjects", None)
    if subjects and hasattr(subjects, "all"):
        names = [_subject_name(subject) for subject in subjects.all()[:6]]
        return [name for name in names if name]
    return []


def _tutor_specialist(tutor):
    names = _tutor_subjects(tutor)[:3]
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


def _known_subjects():
    try:
        Subject = apps.get_model("tutors", "Subject")
        values = list(
            Subject.objects.filter(
                tutors__is_publicly_visible=True,
                tutors__verification_status="approved",
            )
            .values_list("subject_name", flat=True)
            .distinct()
            .order_by("subject_name")
        )
        return values or DEFAULT_SUBJECTS
    except Exception:
        return DEFAULT_SUBJECTS


def _known_locations():
    try:
        Tutor = apps.get_model("tutors", "Tutor")
        values = list(
            Tutor.objects.filter(is_publicly_visible=True, verification_status="approved")
            .exclude(location="")
            .values_list("location", flat=True)
            .distinct()
            .order_by("location")
        )
        return values or DEFAULT_LOCATIONS
    except Exception:
        return DEFAULT_LOCATIONS


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


def _normalize_text(value):
    return re.sub(r"[^a-z0-9+#]+", " ", str(value or "").lower()).strip()


def _skill_terms(value):
    normalized = _normalize_text(value)
    terms = [term for term in normalized.split() if len(term) > 1]
    phrase_map = {
        "python": ["python", "programming", "coding"],
        "backend": ["backend", "api", "database"],
        "python backend": ["python backend", "backend python", "django", "flask", "fastapi", "api", "database"],
        "web": ["web", "html", "css", "javascript", "frontend", "backend", "web development"],
        "css": ["css", "frontend", "html", "web development"],
        "html": ["html", "css", "frontend", "web development"],
        "coding": ["coding", "programming", "python", "javascript", "web development"],
        "programming": ["programming", "coding", "python", "javascript", "c++"],
        "c++": ["c++", "cpp", "programming", "coding"],
        "cpp": ["c++", "cpp", "programming", "coding"],
    }
    if normalized in phrase_map:
        return {normalized, *phrase_map[normalized]}

    expanded = set(terms)
    if normalized:
        expanded.add(normalized)
    for term in list(expanded):
        expanded.update(phrase_map.get(term, []))
    return expanded


def _matches_subject(tutor, subject):
    haystack = " ".join(
        [
            tutor.get("subject", ""),
            tutor.get("specialist", ""),
            " ".join(tutor.get("subjects", [])),
            tutor.get("bio", ""),
        ]
    )
    normalized_haystack = _normalize_text(haystack)
    wanted_terms = _skill_terms(subject)
    return any(_normalize_text(term) in normalized_haystack for term in wanted_terms)


def _matches_query(tutor, query):
    haystack = " ".join(
        [
            tutor.get("name", ""),
            tutor.get("subject", ""),
            tutor.get("specialist", ""),
            " ".join(tutor.get("subjects", [])),
            tutor.get("location", ""),
            tutor.get("bio", ""),
        ]
    )
    query_terms = _skill_terms(query)
    normalized_haystack = _normalize_text(haystack)
    return any(_normalize_text(term) in normalized_haystack for term in query_terms)


def _matches_location(tutor_location, requested_location):
    tutor_text = _normalize_text(tutor_location)
    requested_text = _normalize_text(requested_location)
    aliases = {
        "ph": ["ph", "port harcourt"],
        "port harcourt": ["port harcourt", "ph"],
    }
    requested_aliases = aliases.get(requested_text, [requested_text])
    return any(alias in tutor_text for alias in requested_aliases)


def _latest_pattern_match(normalized_text, choices):
    latest = None
    latest_index = -1
    for value, patterns in choices:
        for pattern in patterns:
            normalized_pattern = _normalize_text(pattern)
            if not normalized_pattern:
                continue
            index = normalized_text.rfind(normalized_pattern)
            if index > latest_index:
                latest = value
                latest_index = index
    return latest
