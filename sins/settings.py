import os
from pathlib import Path
import environ

env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, "changeme-in-dev"),
    ALLOWED_HOSTS=(list, ["*"]),
    LOCATION_ID=(str, "loc1"),
    ROLE_HEADER=(str, "X-Role"),
    FUZZY_HIT_LIMIT=(int, 25),
    RETENTION_DAYS=(int, 365),
    ELASTICSEARCH_HOST=(str, ""),
    KAFKA_BOOTSTRAP=(str, "kafka:9092"),
)

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(env_file=os.path.join(BASE_DIR, ".env"))

DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "customers",
    "audit",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "sins.simpleauth.RoleHeaderMiddleware",
]

ROOT_URLCONF = "sins.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "sins.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# Domain settings
LOCATION_ID = env("LOCATION_ID")
ROLE_HEADER = env("ROLE_HEADER")
FUZZY_HIT_LIMIT = env.int("FUZZY_HIT_LIMIT")
RETENTION_DAYS = env.int("RETENTION_DAYS")
KAFKA_BOOTSTRAP = env("KAFKA_BOOTSTRAP")
ELASTICSEARCH_HOST = env("ELASTICSEARCH_HOST")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
