import os
import logging
import cloudinary
import cloudinary.uploader
from django.conf import settings

logger = logging.getLogger(__name__)


def _ensure_cloudinary_configured():
    cloudinary_url = os.getenv("CLOUDINARY_URL") or getattr(settings, "CLOUDINARY_URL", "")
    if cloudinary_url:
        cloudinary.config(cloudinary_url=cloudinary_url)
    elif getattr(settings, "CLOUDINARY_CLOUD_NAME", None):
        cloudinary.config(
            cloud_name=getattr(settings, "CLOUDINARY_CLOUD_NAME", ""),
            api_key=getattr(settings, "CLOUDINARY_API_KEY", ""),
            api_secret=getattr(settings, "CLOUDINARY_API_SECRET", ""),
        )


def upload_file_in_memory(file_obj, folder="/tutormatch"):
    if file_obj is None:
        return None

    try:
        _ensure_cloudinary_configured()
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        ext = file_obj.name.rsplit(".", 1)[-1].lower() if hasattr(file_obj, "name") and "." in file_obj.name else ""
        resource_type = "image" if ext in {"jpg", "jpeg", "png", "webp", "gif", "bmp"} else "auto"

        response = cloudinary.uploader.upload(
            file_obj,
            folder=folder,
            resource_type=resource_type,
            use_filename=True,
            unique_filename=True,
        )
        url = response.get("secure_url") or response.get("url")
        if not url:
            logger.error("Cloudinary response missing secure_url: %s", response)
        return url
    except Exception as e:
        logger.exception("Cloudinary upload error: %s", e)
        return None


ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "png", "gif", "webp", "bmp", "svg",
    "pdf", "doc", "docx", "xls", "xlsx", "txt", "csv"
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_file(file_obj):
    if not file_obj:
        return False, "No file provided"

    ext = file_obj.name.rsplit(".", 1)[-1].lower() if "." in file_obj.name else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type .{ext} not allowed"

    if hasattr(file_obj, "size") and file_obj.size > MAX_FILE_SIZE:
        return False, "File too large (max 10MB)"

    return True, None


def validate_image(file_obj):
    return validate_file(file_obj)


