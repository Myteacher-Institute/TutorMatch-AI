from django import forms
from .models import Tutor, TutorDocument, Subject
from .geo_data import (
    NIGERIAN_STATES,
    COUNTRIES_BY_CONTINENT,
    DEFAULT_COUNTRY,
)


class TutorProfileForm(forms.ModelForm):
    profile_photo_upload = forms.ImageField(required=False)

    state = forms.ChoiceField(
        choices=[("", "Select state")] + [(s, s) for s in NIGERIAN_STATES],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    local_government = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    country = forms.ChoiceField(
        choices=([("", "Select country")] + [
            (continent, [(c, c) for c in countries])
            for continent, countries in COUNTRIES_BY_CONTINENT.items()
        ]),
        required=False,
        initial=DEFAULT_COUNTRY,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    subjects_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Mathematics, Physics, Chemistry',
            'class': 'tutor-subject-tag-input',
        }),
        help_text='Type a subject and press Enter or comma to add it.',
    )
    years_experience = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',
            'pattern': '[0-9]*',
        }),
    )

    class Meta:
        model = Tutor
        fields = [
            'profile_photo_upload',
            'bio',
            'state',
            'local_government',
            'country',
            'location',
            'rate_period',
            'online_class_fee',
            'physical_class_fee',
            'years_experience',
            'qualifications',
            'account_name',
            'bank_name',
            'account_number',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'qualifications': forms.Textarea(attrs={'rows': 4}),
            'account_name': forms.TextInput(attrs={'placeholder': 'e.g. Samuel Godnews'}),
            'bank_name': forms.TextInput(attrs={'placeholder': 'e.g. Access Bank'}),
            'account_number': forms.TextInput(attrs={'placeholder': 'e.g. 0123456789'}),
            'online_class_fee': forms.TextInput(attrs={
                'type': 'text',
                'inputmode': 'numeric',
                'pattern': '[0-9]*',
            }),
            'physical_class_fee': forms.TextInput(attrs={
                'type': 'text',
                'inputmode': 'numeric',
                'pattern': '[0-9]*',
            }),
        }


class TutorDocumentForm(forms.ModelForm):
    document_file = forms.FileField(required=True)

    class Meta:
        model = TutorDocument
        fields = ['document_type', 'document_file']
