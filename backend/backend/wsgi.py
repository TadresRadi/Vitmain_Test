"""
WSGI config for Vitmain project.
"""
import os
import logging
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Validate security settings on startup
from core.settings_validator import SettingsValidator
logger = logging.getLogger(__name__)

try:
    if not SettingsValidator.validate():
        logger.warning(
            "Security validation found critical errors. "
            "Fix these before deploying to production."
        )
except Exception as e:
    logger.warning(f"Could not validate settings: {str(e)}")

application = get_wsgi_application()