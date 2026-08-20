from django import forms
from .models import Tutor, TutorDocument, Subject, CourseOffer
from .geo_data import (
    NIGERIAN_STATES,
    COUNTRIES_BY_CONTINENT,
    DEFAULT_COUNTRY,
)


class TutorPersonalProfileForm(forms.ModelForm):
    profile_photo_upload = forms.ImageField(required=False)
    subjects_input = forms.CharField(required=False)

    state = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_state'}),
    )
    local_government = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_local_government'}),
    )
    country = forms.ChoiceField(
        choices=([("", "Select country")] + [
            (continent, [(c, c) for c in countries])
            for continent, countries in COUNTRIES_BY_CONTINENT.items()
        ]),
        required=False,
        initial=DEFAULT_COUNTRY,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_country'}),
    )
    years_experience = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',
            'pattern': '[0-9]*',
            'class': 'form-control',
        }),
    )

    class Meta:
        model = Tutor
        fields = [
            'profile_photo_upload',
            'subjects_input',
            'bio',
            'qualifications',
            'years_experience',
            'languages_spoken',
            'country',
            'state',
            'local_government',
            'address',
            'location',
            'teaching_mode',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Tell students about your background and teaching philosophy...'}),
            'qualifications': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Degrees, certifications, or relevant credentials...'}),
            'languages_spoken': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. English, Yoruba, French'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. GRA, Port Harcourt'}),
            'teaching_mode': forms.Select(attrs={'class': 'form-select'}),
        }


class TutorPayoutForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = [
            'payout_method',
            'bank_name',
            'account_name',
            'account_number',
            'payout_schedule',
        ]
        widgets = {
            'payout_method': forms.Select(attrs={'class': 'form-select', 'style': 'width:100%; height:48px; border-radius:12px; border:1px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a;'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Access Bank', 'list': 'nigerian-banks', 'style': 'width:100%; height:48px; border-radius:12px; border:1px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600;'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. John Doe', 'style': 'width:100%; height:48px; border-radius:12px; border:1px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600;'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 0123456789', 'style': 'width:100%; height:48px; border-radius:12px; border:1px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600;'}),
            'payout_schedule': forms.Select(attrs={'class': 'form-select', 'style': 'width:100%; height:48px; border-radius:12px; border:1px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a;'}),
        }


class TutorDocumentForm(forms.ModelForm):
    document_file = forms.FileField(required=True)

    class Meta:
        model = TutorDocument
        fields = ['document_type', 'document_file']


class CourseOfferForm(forms.ModelForm):
    STEM_CATEGORY_CHOICES = [
        ("Science", "🔬 Science (Physics, Chemistry, Biology)"),
        ("Technology & Coding", "💻 Technology & Coding (Python, Web, AI)"),
        ("Engineering & Robotics", "⚙️ Engineering & Robotics (CAD, Tech Drawing, Hardware)"),
        ("Mathematics & Further Maths", "📐 Mathematics & Further Maths (Calculus, WAEC/JAMB)"),
        ("Digital Skills & Design", "🎨 Digital Skills & Design (UI/UX, Graphics, Data Analysis)"),
        ("Other Academic", "📚 Other Academic Disciplines"),
    ]

    category = forms.ChoiceField(
        choices=STEM_CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-select",
            "style": "width:100%; height:48px; border-radius:12px; border:1.5px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"
        })
    )

    class Meta:
        model = CourseOffer
        fields = [
            "title",
            "category",
            "level",
            "currency",
            "monthly_fee",
            "duration_months",
            "sessions_per_week",
            "hours_per_session",
            "max_students",
            "delivery_mode",
            "online_platform",
            "physical_location",
            "schedule_days_times",
            "description",
            "syllabus",
            "rules",
            "requirements",
            "cover_image",
            "cover_image_file",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Python Programming, Further Mathematics, UI/UX Design", "style": "width:100%; height:48px; border-radius:12px; border:1.5px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "level": forms.Select(attrs={"class": "form-select", "style": "width:100%; height:48px; border-radius:12px; border:1.5px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "currency": forms.Select(attrs={"class": "form-select", "style": "width:100%; height:48px; border-radius:12px; border:1.5px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "monthly_fee": forms.NumberInput(attrs={"class": "form-control", "placeholder": "25000", "min": "1000", "step": "500", "style": "width:100%; height:48px; border-radius:12px; border:1.5px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "duration_months": forms.NumberInput(attrs={"class": "form-control", "placeholder": "1", "min": "1", "max": "12", "style": "width:100%; height:48px; border-radius:12px; border:1.5px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "sessions_per_week": forms.NumberInput(attrs={"class": "form-control", "placeholder": "3", "min": "1", "max": "7", "style": "width:100%; height:48px; border-radius:12px; border:1.5px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "hours_per_session": forms.NumberInput(attrs={"class": "form-control", "placeholder": "2", "min": "1", "max": "8", "style": "width:100%; height:48px; border-radius:12px; border:1.5px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "max_students": forms.NumberInput(attrs={"class": "form-control", "placeholder": "5", "min": "1", "style": "width:100%; height:48px; border-radius:12px; border:1.5px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "delivery_mode": forms.Select(attrs={"class": "form-select", "style": "width:100%; height:48px; border-radius:12px; border:1.5px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "online_platform": forms.Select(attrs={"class": "form-select", "style": "width:100%; height:48px; border-radius:12px; border:1.5px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "physical_location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Address details if Physical class", "style": "width:100%; height:48px; border-radius:12px; border:1.5px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "schedule_days_times": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Mondays & Wednesdays, 4:00 PM - 6:00 PM", "style": "width:100%; height:48px; border-radius:12px; border:1.5px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Detailed description of what students will learn in this STEM / Digital Skills course...", "style": "width:100%; border-radius:12px; border:1.5px solid #cbd5e1; padding:12px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "syllabus": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Week 1: Introduction & Environment Setup\nWeek 2: Data Structures & Core Logic\nWeek 3: Real-World Exercises & Projects\nWeek 4: Review & Certification Prep", "style": "width:100%; border-radius:12px; border:1.5px solid #cbd5e1; padding:12px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "rules": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "e.g. 80% attendance required, late policy...", "style": "width:100%; border-radius:12px; border:1.5px solid #cbd5e1; padding:12px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "requirements": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "e.g. Laptop, notebook, basic computer literacy...", "style": "width:100%; border-radius:12px; border:1.5px solid #cbd5e1; padding:12px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "cover_image": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://images.unsplash.com/...", "style": "width:100%; height:48px; border-radius:12px; border:1.5px solid #cbd5e1; padding:10px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
            "cover_image_file": forms.ClearableFileInput(attrs={"class": "form-control", "style": "width:100%; height:48px; border-radius:12px; border:1.5px solid #cbd5e1; padding:8px 16px; font-size:14px; font-weight:600; color:#0f172a; background:#ffffff;"}),
        }


