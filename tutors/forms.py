from django import forms
from .models import Tutor, TutorDocument, Subject


class TutorProfileForm(forms.ModelForm):
    profile_photo_upload = forms.ImageField(required=False)

    class Meta:
        model = Tutor
        fields = [
            'profile_photo_upload',
            'bio',
            'location',
            'hourly_rate',
            'years_experience',
            'subjects',
            'qualifications',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'qualifications': forms.Textarea(attrs={'rows': 4}),
            'subjects': forms.CheckboxSelectMultiple(),
        }


class TutorDocumentForm(forms.ModelForm):
    document_file = forms.FileField(required=True)

    class Meta:
        model = TutorDocument
        fields = ['document_type', 'document_file']
