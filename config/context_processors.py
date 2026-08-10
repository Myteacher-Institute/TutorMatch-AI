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

    default_title = "MyteacherConnect | Find Tutor & Best Home Tutors in PH, Lagos & Abuja"
    default_description = "Find the best verified home and online tutors on MyteacherConnect (MyTeacher / MyTeach). Connect with top background-checked private tutors in Port Harcourt (PH), Lagos, Abuja, and across Nigeria for WAEC, JAMB, Math, Sciences & coding."
    default_keywords = "find tutor, tutor in ph, best tutor, myteacher, myteach, myteacherconnect, connect, tutor in port harcourt, home tutors nigeria, find private tutor lagos, abuja home lesson teacher, hire best tutor, waec jamb tutor, best home tutor in ph, online math teacher nigeria, private lesson teacher, connect with tutor, science tutor port harcourt, math tutor ph"
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
