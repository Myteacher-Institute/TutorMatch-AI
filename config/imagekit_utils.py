import uuid
from django.conf import settings

try:
    from imagekitio import ImageKit
    IMAGEKIT_AVAILABLE = True
except ImportError:
    IMAGEKIT_AVAILABLE = False
    ImageKit = None


def get_imagekit_client():
    if not IMAGEKIT_AVAILABLE:
        return None
    private_key = getattr(settings, "IMAGEKIT_PRIVATE_KEY", "")
    if not private_key:
        return None
    return ImageKit(private_key=private_key)


def upload_to_imagekit(file_data, filename, folder="/tutormatch"):
    imagekit = get_imagekit_client()
    if imagekit is None:
        raise ValueError("ImageKit is not configured. Please set IMAGEKIT_PRIVATE_KEY.")

    safe_filename = filename.replace(" ", "_")
    unique_filename = f"{uuid.uuid4()}_{safe_filename}"

    return imagekit.files.upload(
        file=file_data,
        file_name=unique_filename,
        folder=folder,
        use_unique_file_name=False,
    )


def upload_file_in_memory(file_obj, folder="/tutormatch"):
    if file_obj is None:
        return None

    file_data = file_obj.read()
    original_filename = file_obj.name
    if hasattr(file_obj, "seek"):
        file_obj.seek(0)

    response = upload_to_imagekit(file_data, original_filename, folder)

    if response:
        return response.url
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
