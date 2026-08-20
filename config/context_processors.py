import os


def seo_context(request):
    """
    Global SEO context processor supplying site URL, canonical URL,
    Google Search Console verification tag, and social share metadata.
    """
    site_url = os.getenv("SITE_URL", "https://myteacherconnect.org").rstrip("/")
    google_verification = os.getenv("GOOGLE_SITE_VERIFICATION", "")

    if request:
        canonical_url = f"{site_url}{request.path}"
    else:
        canonical_url = site_url

    default_title = "MyteacherConnect | Best STEM & Digital Skills Tutors in Nigeria"
    default_description = "Find verified STEM (Science, Technology, Engineering, Mathematics) & Digital Skills home and online tutors in Port Harcourt (PH), Lagos, Abuja, and across Nigeria on MyteacherConnect. Connect with experts in Python, Web Dev, Further Maths, Physics, Robotics & UI/UX."
    default_keywords = "STEM tutors Nigeria, python tutor for kids, STEM tutors in ph, math tutor lagos, physics tutor abuja, further mathematics tutor, robotics tutor nigeria, ui ux design tutor, coding for kids nigeria, myteacherconnect, stem education nigeria"
    default_image = f"{site_url}/static/images/logos/myteacherconnect-logo-blue-transparent.png"

    return {
        "SITE_URL": site_url,
        "CANONICAL_URL": canonical_url,
        "GOOGLE_SITE_VERIFICATION": google_verification,
        "DEFAULT_SEO_TITLE": default_title,
        "DEFAULT_SEO_DESCRIPTION": default_description,
        "DEFAULT_SEO_KEYWORDS": default_keywords,
        "DEFAULT_SEO_IMAGE": default_image,
        "BRAND_NAME": "MyteacherConnect",
        "BRAND_ALIASES": "MyTeacher, MyTeach, MyteacherConnect, TutorMatch AI",
    }
