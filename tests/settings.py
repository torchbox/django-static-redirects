import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = ["static_redirect", "tests"]

MIDDLEWARE = [
    "static_redirect.StaticRedirectMiddleware",
    "django.middleware.common.CommonMiddleware",
]

SECRET_KEY = "abcde12345"

ROOT_URLCONF = "tests.urls"

STATIC_REDIRECT_FILES = [
    os.path.join(BASE_DIR, "tests/redirects/redirects.csv")
]
