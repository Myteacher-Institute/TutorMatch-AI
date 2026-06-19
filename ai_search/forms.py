from django import forms


SUBJECT_CHOICES = [
    ("", "Any subject"),
    ("Mathematics", "Mathematics"),
    ("English", "English"),
    ("Physics", "Physics"),
    ("Chemistry", "Chemistry"),
    ("Biology", "Biology"),
    ("Economics", "Economics"),
]

LOCATION_CHOICES = [
    ("", "Any location"),
    ("GRA", "GRA"),
    ("Rumuola", "Rumuola"),
    ("Trans Amadi", "Trans Amadi"),
    ("D-Line", "D-Line"),
    ("Ada George", "Ada George"),
    ("Woji", "Woji"),
]


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
    subject = forms.ChoiceField(required=False, choices=SUBJECT_CHOICES)
    location = forms.ChoiceField(required=False, choices=LOCATION_CHOICES)
    min_price = forms.IntegerField(required=False, min_value=0)
    max_price = forms.IntegerField(required=False, min_value=0)
    min_experience = forms.IntegerField(required=False, min_value=0)
