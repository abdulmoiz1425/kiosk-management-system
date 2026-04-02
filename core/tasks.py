"""
Celery tasks for async file operations.
Views save the file synchronously first (temp), then this task
moves/processes it — keeping HTTP responses fast.
"""
import os
import logging
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def move_to_nas(self, temp_path: str, rel_path: str):
    """
    Moves a file from local temp storage to the NAS mount.
    Used when a file was written locally because NAS was unavailable
    at upload time — retried automatically once NAS comes back.
    """
    from core.storage import _is_nas_available, get_full_path

    if not _is_nas_available():
        logger.warning("NAS not available, retrying task move_to_nas (attempt %s)", self.request.retries)
        raise self.retry()

    nas_full = os.path.join(str(settings.NAS_MOUNT_PATH), rel_path)
    nas_dir = os.path.dirname(nas_full)
    os.makedirs(nas_dir, exist_ok=True)

    if os.path.exists(temp_path):
        import shutil
        shutil.move(temp_path, nas_full)
        logger.info("Moved %s → %s (NAS)", temp_path, nas_full)
    else:
        logger.error("Temp file not found: %s", temp_path)


@shared_task
def cleanup_old_temp_files():
    """
    Periodic task: removes temp files older than 7 days from MEDIA_ROOT
    that have already been moved to NAS.
    """
    import time
    from core.storage import _is_nas_available

    if not _is_nas_available():
        return

    media_root = str(settings.MEDIA_ROOT)
    cutoff = time.time() - (7 * 86400)
    removed = 0

    for dirpath, _, filenames in os.walk(media_root):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            rel = os.path.relpath(fpath, media_root)
            nas_path = os.path.join(str(settings.NAS_MOUNT_PATH), rel)
            if os.path.exists(nas_path) and os.path.getmtime(fpath) < cutoff:
                os.remove(fpath)
                removed += 1

    logger.info("cleanup_old_temp_files: removed %d files", removed)
    return removed
