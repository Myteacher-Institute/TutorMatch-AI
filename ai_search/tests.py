from unittest.mock import patch

from django.test import SimpleTestCase

from .assistant import _merge_intent_state
from .services import _extract_with_rules, search_tutors


class SearchIntentTests(SimpleTestCase):
    def test_rule_extraction_prefers_latest_subject_mention(self):
        intent = _extract_with_rules("I want to learn Python. Now I need a math tutor.")

        self.assertEqual(intent["subject"], "Mathematics")

    def test_conversation_state_uses_latest_message_as_active_query(self):
        previous_state = {
            "subject": "Python",
            "level": "Beginner",
            "location": "GRA",
            "schedule": "weekends",
        }
        user_messages = [
            "I want to learn Python as a beginner in GRA.",
            "I need a math tutor now.",
        ]

        with patch("ai_search.assistant.extract_search_intent", side_effect=_extract_with_rules):
            state = _merge_intent_state(previous_state, user_messages)

        self.assertEqual(state["query_text"], "I need a math tutor now.")
        self.assertEqual(state["subject"], "Mathematics")
        self.assertEqual(state["level"], "")
        self.assertEqual(state["location"], "GRA")

    def test_specific_framework_search_does_not_return_generic_python_tutor(self):
        tutors = [
            {
                "id": 1,
                "name": "Python Tutor",
                "subject": "Python",
                "subjects": ["Python"],
                "specialist": "Python Programming",
                "level": "Beginner",
                "location": "Online",
                "rate": 5000,
                "experience": 2,
                "rating": 4.7,
                "verified": True,
                "bio": "Teaches Python fundamentals and coding basics.",
            },
            {
                "id": 2,
                "name": "Django Tutor",
                "subject": "Python",
                "subjects": ["Python"],
                "specialist": "Django Backend Development",
                "level": "Intermediate",
                "location": "Online",
                "rate": 8000,
                "experience": 5,
                "rating": 4.9,
                "verified": True,
                "bio": "Builds APIs with Django, databases, and deployment workflows.",
            },
        ]

        with patch("ai_search.services._load_database_tutors", return_value=tutors):
            results = search_tutors({"query_text": "django tutor", "subject": "Django", "location": "Online"})

        self.assertEqual([tutor["name"] for tutor in results], ["Django Tutor"])

    def test_python_backend_search_does_not_return_python_basics_only(self):
        tutors = [
            {
                "id": 1,
                "name": "Python Basics Tutor",
                "subject": "Python",
                "subjects": ["Python"],
                "specialist": "Python Programming",
                "level": "Beginner",
                "location": "Online",
                "rate": 5000,
                "experience": 2,
                "rating": 4.7,
                "verified": True,
                "bio": "Teaches Python syntax, loops, functions, and beginner coding.",
            },
            {
                "id": 2,
                "name": "Backend Tutor",
                "subject": "Python",
                "subjects": ["Python"],
                "specialist": "Python Backend Development",
                "level": "Intermediate",
                "location": "Online",
                "rate": 8000,
                "experience": 5,
                "rating": 4.9,
                "verified": True,
                "bio": "Teaches APIs, databases, Django, Flask, and FastAPI.",
            },
        ]

        with patch("ai_search.services._load_database_tutors", return_value=tutors):
            results = search_tutors(
                {"query_text": "python backend tutor", "subject": "Python Backend", "location": "Online"}
            )

        self.assertEqual([tutor["name"] for tutor in results], ["Backend Tutor"])
