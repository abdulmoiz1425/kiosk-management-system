"""
Wafaa Tech — File Storage Handler
Saves uploads to:
  NAS (production):  {NAS_MOUNT_PATH}/{kiosk_name}/{YYYY-MM-DD}/{file_type}/{filename}
  Local (dev/fallback): {MEDIA_ROOT}/{kiosk_name}/{YYYY-MM-DD}/{file_type}/{filename}

Only the relative path under the base is stored in the database.
Falls back to local MEDIA_ROOT automatically when NAS is not mounted.
"""
import os
import logging
from datetime import date
from django.conf import settings

logger = logging.getLogger(__name__)


def _is_nas_available() -> bool:
    """Check whether the NAS mount path exists and is writable."""
    nas_path = getattr(settings, 'NAS_MOUNT_PATH', None)
    if not nas_path:
        return False
    return os.path.isdir(nas_path) and os.access(nas_path, os.W_OK)


def get_base_path() -> str:
    """
    Returns the active base storage path.
    Uses NAS if available, otherwise falls back to MEDIA_ROOT.
    """
    if _is_nas_available():
        return str(settings.NAS_MOUNT_PATH)
    return str(settings.MEDIA_ROOT)


def get_upload_path(kiosk_name: str, file_type: str, filename: str) -> str:
    """
    Returns the relative storage path for a file.
    Structure: {kiosk_name}/{YYYY-MM-DD}/{file_type}/{filename}
    e.g. kiosk_1/2026-04-02/checkin/1712046000.jpg
    """
    safe_kiosk = (
        kiosk_name
        .replace(' ', '_')
        .replace('/', '-')
        .replace('\\', '-')
    )
    today = date.today().strftime('%Y-%m-%d')
    return os.path.join(safe_kiosk, today, file_type, filename)


def get_full_path(relative_path: str) -> str:
    """Returns the absolute path on disk for a relative storage path."""
    return os.path.join(get_base_path(), relative_path)


def ensure_directory(relative_path: str) -> str:
    """
    Creates the directory tree for the given relative path if missing.
    Returns the full absolute path of the file (not the directory).
    """
    full_path = get_full_path(relative_path)
    directory = os.path.dirname(full_path)
    os.makedirs(directory, exist_ok=True)
    return full_path


def save_upload(file_obj, kiosk_name: str, file_type: str) -> str:
    """
    Saves an uploaded file to the structured storage location.
    Returns the relative path stored in the DB.

    Usage:
        rel_path = save_upload(request.FILES['photo'], kiosk.name, 'checkin')
    """
    ext = os.path.splitext(file_obj.name)[1].lower()
    # Use timestamp to avoid collisions (multiple uploads same day)
    import time
    filename = f"{int(time.time())}{ext}"
    rel_path = get_upload_path(kiosk_name, file_type, filename)
    full_path = ensure_directory(rel_path)

    using_nas = _is_nas_available()
    storage_label = "NAS" if using_nas else "local media"
    logger.info("Saving %s upload → %s (%s)", file_type, full_path, storage_label)

    with open(full_path, 'wb+') as dest:
        for chunk in file_obj.chunks():
            dest.write(chunk)

    return rel_path


def get_media_url(relative_path: str) -> str:
    """Returns a URL for serving a stored file through Django's MEDIA_URL."""
    if not relative_path:
        return ''
    # Normalize separators for URLs
    url_path = relative_path.replace('\\', '/')
    return f"{settings.MEDIA_URL}{url_path}"
