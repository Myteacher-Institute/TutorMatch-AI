from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "review"]
        widgets = {
            "rating": forms.RadioSelect(
                choices=[(5, "5"), (4, "4"), (3, "3"), (2, "2"), (1, "1")]
            ),
            "review": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Share how the lesson went, what worked well, and anything other students should know.",
                }
            ),
        }

    def clean_rating(self):
        rating = self.cleaned_data["rating"]
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Choose a rating from 1 to 5.")
        return rating
