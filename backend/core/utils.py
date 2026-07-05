import logging

from core.models import AuditLog

logger = logging.getLogger(__name__)


def log_user_activity(user, action, details=None):
    if details is None:
        details = {}

    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            details=details,
        )
    except Exception:
        logger.exception("Failed to log user activity (user=%s, action=%s)", getattr(user, "id", None), action)
