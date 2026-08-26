"""Settings for the Mailtea example: one app, sqlite, and nothing else.

Credentials come from the environment, never from this file. `.env` is read on
startup so that `cp .env.example .env` is the whole setup step.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# --- Mailtea ---------------------------------------------------------------

MAILTEA_API_KEY = os.environ.get("MAILTEA_API_KEY", "")

# Only set for local dev or a self-hosted Mailtea. Empty means the SDK's
# default, https://api.mailtea.app.
MAILTEA_API_BASE_URL = os.environ.get("MAILTEA_API_BASE_URL") or None

# Must be an address on a domain you have verified in Mailtea.
MAILTEA_FROM = os.environ.get("MAILTEA_FROM", "Acme <hello@acme.com>")

# --- Django ----------------------------------------------------------------

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-not-for-production")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = ["notify"]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

USE_TZ = True
