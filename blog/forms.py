from django import forms
from .models import BlogPost, BlogCategory


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = [
            "title",
            "slug",
            "category",
            "excerpt",
            "content",
            "image",
            "image_url",
            "meta_title",
            "meta_description",
            "meta_keywords",
            "status",
            "is_featured",
            "estimated_read_time",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control mtc-input",
                "placeholder": "e.g. 10 Proven Strategies to Ace WAEC & JAMB in Nigeria (2026)",
                "required": True,
                "id": "id_blog_title"
            }),
            "slug": forms.TextInput(attrs={
                "class": "form-control mtc-input",
                "placeholder": "e.g. how-to-ace-waec-jamb-nigeria",
                "id": "id_blog_slug"
            }),
            "category": forms.Select(attrs={
                "class": "form-select mtc-select",
                "id": "id_blog_category"
            }),
            "excerpt": forms.Textarea(attrs={
                "class": "form-control mtc-textarea",
                "rows": 3,
                "placeholder": "A brief, compelling summary (1-2 sentences) of what the reader will learn...",
                "required": True,
                "id": "id_blog_excerpt"
            }),
            "content": forms.Textarea(attrs={
                "class": "form-control mtc-textarea",
                "rows": 16,
                "placeholder": "Write your full blog post here. You can use standard HTML (<h2>, <p>, <ul>, <strong>, <blockquote>) or formatted text...",
                "required": True,
                "id": "id_blog_content"
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control mtc-input-file",
                "accept": "image/*",
                "id": "id_blog_image"
            }),
            "image_url": forms.URLInput(attrs={
                "class": "form-control mtc-input",
                "placeholder": "https://example.com/images/educational-banner.jpg",
                "id": "id_blog_image_url"
            }),
            "meta_title": forms.TextInput(attrs={
                "class": "form-control mtc-input",
                "placeholder": "SEO Title tag (e.g. Best Home Tutors in Lagos & PH | MyteacherConnect)",
                "id": "id_blog_meta_title"
            }),
            "meta_description": forms.Textarea(attrs={
                "class": "form-control mtc-textarea",
                "rows": 2,
                "placeholder": "Meta description for Google search snippet (150-160 characters recommended)",
                "id": "id_blog_meta_description"
            }),
            "meta_keywords": forms.TextInput(attrs={
                "class": "form-control mtc-input",
                "placeholder": "waec tutor, jamb prep, private teacher lagos, port harcourt math tutor",
                "id": "id_blog_meta_keywords"
            }),
            "status": forms.Select(attrs={
                "class": "form-select mtc-select",
                "id": "id_blog_status"
            }),
            "is_featured": forms.CheckboxInput(attrs={
                "class": "form-check-input mtc-checkbox",
                "id": "id_blog_is_featured"
            }),
            "estimated_read_time": forms.NumberInput(attrs={
                "class": "form-control mtc-input",
                "min": 1,
                "placeholder": "3",
                "id": "id_blog_read_time"
            }),
        }


class BlogCategoryForm(forms.ModelForm):
    class Meta:
        model = BlogCategory
        fields = ["name", "slug", "description", "icon"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control mtc-input",
                "placeholder": "e.g. Exam Preparation",
                "required": True,
            }),
            "slug": forms.TextInput(attrs={
                "class": "form-control mtc-input",
                "placeholder": "e.g. exam-preparation",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control mtc-textarea",
                "rows": 2,
                "placeholder": "Short description of this category...",
            }),
            "icon": forms.TextInput(attrs={
                "class": "form-control mtc-input",
                "placeholder": "fa-graduation-cap",
            }),
        }
