import cloudinary
import cloudinary.uploader
from django.conf import settings

def upload_file_in_memory(file_obj, folder="/tutormatch"):
    if file_obj is None:
        return None

    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
            
        response = cloudinary.uploader.upload(
            file_obj,
            folder=folder,
            resource_type="auto"
        )
        return response.get("secure_url")
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
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

