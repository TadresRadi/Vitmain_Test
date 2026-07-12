import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import logging.config
import sys





# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
MEDIA_ROOT = BASE_DIR / "media"
STATIC_ROOT = BASE_DIR / "staticfiles"

LOG_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
STATIC_ROOT.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
# Load environment variables
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Replicate API token (used for AI-generated images)
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")

# Stability AI token (used for AI-generated images)
STABILITY_API_TOKEN = os.environ.get("STABILITY_API_TOKEN")

# DeepAI token (used for AI-generated images)
DEEPAI_API_TOKEN = os.environ.get("DEEPAI_API_TOKEN")
SENTRY_DSN = os.environ.get("SENTRY_DSN")

if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            traces_sample_rate=float(
                os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.0")
            ),
            # Do NOT send PII (user IPs, cookies, request bodies) to Sentry.
            # This is required for GDPR/CCPA compliance.
            send_default_pii=False,
        )
    except ImportError:
        pass
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL', '')

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY env var is required")

DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS if h.strip()]

# Add ngrok domain for development
if DEBUG:
    ALLOWED_HOSTS.extend([
        '127.0.0.1',
        'localhost',
        '127.0.0.1:8000',
        'localhost:8000',
        "host.docker.internal",
    ])
    # Only add ngrok if explicitly configured
    ngrok_url = os.environ.get('NGROK_URL')
    if ngrok_url:
        ALLOWED_HOSTS.append(ngrok_url)

if not ALLOWED_HOSTS and not DEBUG:
    raise RuntimeError("ALLOWED_HOSTS env var is required when DEBUG=false")

# Application definition
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'corsheaders',
    'rest_framework_simplejwt.token_blacklist',
    'django_prometheus',
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Local apps
    'core',
    'users',
    'subscriptions',
    'onboarding',
    'chat',
    'support',
    'portfolio.apps.PortfolioConfig',
    'payments.apps.PaymentsConfig',
]

ENABLE_PROMETHEUS = (
    os.environ.get("ENABLE_PROMETHEUS", "false").lower() == "true"
)

MIDDLEWARE = [
    'core.middleware.request_id.RequestIDMiddleware',
    'core.middleware.slow_query.QueryTimingMiddleware',
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # CORS Middleware MUST be at the top to handle preflight requests
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # NEW: Security middleware (uncomment in security hardening phase)
    # 'core.https_middleware.HTTPSEnforcerMiddleware',
    # 'core.https_middleware.SecureProxyHeadersMiddleware',
    # 'core.security_headers.SecurityHeadersMiddleware',
    # 'core.security_headers.CSPHeaderMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.validation_middleware.RequestValidationMiddleware',
    'core.audit_middleware.AuditLoggingMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
ROOT_URLCONF = 'backend.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Database configuration (PostgreSQL Only)
DB_NAME = os.environ.get('DB_NAME', 'vitmain_db')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('DB_PORT', '5432')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}
# ============================================================================
# CACHING CONFIGURATION
# ============================================================================
# Used for CSRF tokens, rate limiting, OAuth state, etc.

REDIS_URL = os.environ.get("REDIS_URL")


if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "vitmain-cache",
            "TIMEOUT": 3600,
        }
    }


# ============================================================================
# CORS Configuration
# ============================================================================

# Read CORS allowed origins from environment
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

# In development, add local defaults if not specified
if DEBUG and not CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

# CORS credentials and other settings
CORS_ALLOW_ALL_ORIGINS = os.environ.get("CORS_ALLOW_ALL_ORIGINS", "false").lower() == "true"
CORS_ALLOW_CREDENTIALS = os.environ.get("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

# Additional CORS settings for preflight requests
# Additional CORS settings for preflight requests
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# In development, optionally allow an ngrok tunnel via env var (NGROK_ORIGIN).
if DEBUG:
    ngrok_origin = os.environ.get('NGROK_ORIGIN')
    if ngrok_origin and ngrok_origin not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append(ngrok_origin)

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # APIKeyAuthentication MUST come before JWTAuthentication.
        # DRF stops at the first AuthenticationFailed, so if JWT runs
        # first, it raises InvalidToken for API keys and blocks APIKeyAuth.
        # APIKeyAuth returns None for non-API-key tokens (JWTs), letting
        # JWTAuthentication handle them.
        'core.auth_backends.APIKeyAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_EXCEPTION_HANDLER': 'core.exception_handlers.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
# SimpleJWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Django Allauth Settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Disabled for Google OAuth
ACCOUNT_USERNAME_REQUIRED = False

ACCOUNT_UNIQUE_EMAIL = True

# Custom Adapters
ACCOUNT_ADAPTER = 'users.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'users.adapters.CustomSocialAccountAdapter'

# Social Account Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        },
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'key': '',
        },
    }
}

# Google OAuth Settings
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
USE_I18N = True
USE_TZ = True

# URL handling
APPEND_SLASH = True

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

# HTTPS/SSL Settings
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "false").lower() == "true"
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "0" if DEBUG else "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS",
    str(not DEBUG)
).lower() == "true"
SECURE_HSTS_PRELOAD = os.environ.get("SECURE_HSTS_PRELOAD", "false").lower() == "true"

# Cookie Security
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", str(not DEBUG)).lower() == "true"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", str(not DEBUG)).lower() == "true"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

if DEBUG and not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

# Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
VODAFONE_TESTING_PRICE = float(os.environ.get("VODAFONE_TESTING_PRICE", "5.00"))
VODAFONE_RECEIVER_NUMBER = os.environ.get("VODAFONE_RECEIVER_NUMBER", "")
VODAFONE_WEBHOOK_SECRET_TOKEN = os.environ.get("VODAFONE_WEBHOOK_SECRET_TOKEN", "")

# Validate only outside development/testing
# Validate only outside development/testing.
# Detect both `manage.py test` and `pytest` (including `python -m pytest`).
_is_test_run = (
    "test" in sys.argv
    or any("pytest" in str(arg) for arg in sys.argv)
)
if not DEBUG and not _is_test_run:
    if not VODAFONE_WEBHOOK_SECRET_TOKEN:
        raise RuntimeError("VODAFONE_WEBHOOK_SECRET_TOKEN env var is required")

    if not VODAFONE_RECEIVER_NUMBER:
        raise RuntimeError("VODAFONE_RECEIVER_NUMBER env var is required")
# ============================================================================
# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

USE_JSON_LOGS = os.environ.get("USE_JSON_LOGS", "false").lower() == "true"
if USE_JSON_LOGS:
    try:
        from pythonjsonlogger import jsonlogger  # noqa: F401
    except ImportError:
        # python-json-logger not installed; fall back to text logs
        USE_JSON_LOGS = False

# Slow query threshold (requests slower than this are logged to db.log)
SLOW_QUERY_THRESHOLD_MS = int(os.environ.get("SLOW_QUERY_THRESHOLD_MS", "200"))

_json_formatter_config = {
    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
    "fmt": "%(levelname)s %(asctime)s %(module)s %(message)s",
}
_verbose_formatter_config = {
    "format": "{levelname} {asctime} [req:{request_id}] {module} {message}",
    "style": "{",
    "datefmt": "%Y-%m-%d %H:%M:%S",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": _json_formatter_config,
        "verbose": _verbose_formatter_config,
        "simple": {
            "format": "{levelname} {asctime} [req:{request_id}] {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "request_id": {
            "()": "core.log_filters.RequestIDFilter",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json" if USE_JSON_LOGS else "simple",
            "filters": ["request_id"],
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.environ.get("LOG_FILE", str(LOG_DIR / "django.log")),
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
            "formatter": "json" if USE_JSON_LOGS else "verbose",
            "filters": ["request_id"],
        },
        "security_file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.environ.get("SECURITY_LOG_FILE", str(LOG_DIR / "security.log")),
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
            "formatter": "json" if USE_JSON_LOGS else "verbose",
            "filters": ["request_id"],
        },
        "db_file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.environ.get("DB_LOG_FILE", str(LOG_DIR / "db.log")),
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 3,
            "formatter": "json" if USE_JSON_LOGS else "verbose",
            "filters": ["request_id"],
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "security_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["db_file", "console"],
            "level": "WARNING",
            "propagate": False,
        },
        "users": {
            "handlers": ["console", "file", "security_file"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "allauth": {
            "handlers": ["console", "file", "security_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING)
# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

# Email Backend
if DEBUG:
    # Development: Print emails to console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Production: Use SMTP
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Default from email
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@vitmain.com')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'server@vitmain.com')
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"