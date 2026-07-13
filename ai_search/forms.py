from django import forms


FALLBACK_SUBJECTS = [
    "Mathematics",
    "English",
    "Physics",
    "Chemistry",
    "Biology",
    "Economics",
]

FALLBACK_LOCATIONS = [
    "GRA",
    "Rumuola",
    "Trans Amadi",
    "D-Line",
    "Ada George",
    "Woji",
]


def _choice_list(empty_label, values):
    clean_values = [value for value in values if value]
    return [("", empty_label), *[(value, value) for value in clean_values]]


def subject_choices():
    try:
        from tutors.models import Subject

        subjects = (
            Subject.objects.filter(
                tutors__is_publicly_visible=True,
                tutors__verification_status="approved",
            )
            .values_list("subject_name", flat=True)
            .distinct()
            .order_by("subject_name")
        )
        values = list(subjects) or FALLBACK_SUBJECTS
    except Exception:
        values = FALLBACK_SUBJECTS
    return _choice_list("Any subject", values)


def location_choices():
    try:
        from tutors.models import Tutor

        locations = (
            Tutor.objects.filter(is_publicly_visible=True, verification_status="approved")
            .exclude(location="")
            .values_list("location", flat=True)
            .distinct()
            .order_by("location")
        )
        values = list(locations) or FALLBACK_LOCATIONS
    except Exception:
        values = FALLBACK_LOCATIONS
    return _choice_list("Any location", values)


class TutorSearchForm(forms.Form):
    q = forms.CharField(
        label="Describe your tutor need",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "I need a Mathematics tutor for SS2 in GRA Port Harcourt who can teach weekends.",
            }
        ),
    )
    subject = forms.ChoiceField(required=False, choices=[])
    location = forms.ChoiceField(required=False, choices=[])
    min_price = forms.IntegerField(required=False, min_value=0)
    max_price = forms.IntegerField(required=False, min_value=0)
    min_experience = forms.IntegerField(required=False, min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"].choices = subject_choices()
        self.fields["location"].choices = location_choices()

        select_attrs = {
            "style": "width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px; font-size: 13px; outline: none; background: white; cursor: pointer;",
        }
        self.fields["subject"].widget.attrs.update(select_attrs)
        self.fields["location"].widget.attrs.update(select_attrs)
