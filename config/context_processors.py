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

    default_title = "MyteacherConnect | Find Verified Home & Online Tutors in Nigeria"
    default_description = "Connect with background-checked home and online tutors in Nigeria for Mathematics, English, Sciences, WAEC/JAMB preparation, and coding."
    default_image = f"{site_url}/static/images/logos/myteacherconnect-logo-blue-transparent.png"

    return {
        "SITE_URL": site_url,
        "CANONICAL_URL": canonical_url,
        "GOOGLE_SITE_VERIFICATION": google_verification,
        "DEFAULT_SEO_TITLE": default_title,
        "DEFAULT_SEO_DESCRIPTION": default_description,
        "DEFAULT_SEO_IMAGE": default_image,
    }
