"""
WSGI config for Vitmain project.

In production (DEBUG=False), the settings validator runs at startup and
REFUSES TO BOOT if critical security errors are found. This prevents a
misconfigured deployment from serving traffic.

To bypass in emergencies (NOT RECOMMENDED), set SKIP_SETTINGS_VALIDATION=true
in the environment.
"""
import os
import logging
from django.core.wsgi import get_wsgi_application
from django.conf import settings as django_settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Validate security settings on startup
from core.settings_validator import SettingsValidator
logger = logging.getLogger(__name__)

try:
    validation_passed = SettingsValidator.validate()
    if not validation_passed:
        if not django_settings.DEBUG and not os.environ.get('SKIP_SETTINGS_VALIDATION'):
            # In production, fail-closed: refuse to boot.
            logger.error("=" * 80)
            logger.error("FATAL: Security validation found critical errors.")
            logger.error("Refusing to boot in production mode.")
            logger.error("Fix the errors above, or set SKIP_SETTINGS_VALIDATION=true")
            logger.error("to bypass (NOT RECOMMENDED).")
            logger.error("=" * 80)
            raise RuntimeError(
                "Security validation found critical errors. "
                "Refusing to boot in production mode. "
                "Set SKIP_SETTINGS_VALIDATION=true to bypass (NOT RECOMMENDED)."
            )
        else:
            # In DEBUG mode, just warn.
            logger.warning(
                "Security validation found critical errors. "
                "Fix these before deploying to production."
            )
except RuntimeError:
    raise
except Exception as e:
    logger.warning(f"Could not validate settings: {str(e)}")

application = get_wsgi_application()