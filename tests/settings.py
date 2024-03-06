import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = ["static_redirects", "tests"]

MIDDLEWARE = [
    "static_redirects.StaticRedirectsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

SECRET_KEY = "abcde12345"

ROOT_URLCONF = "tests.urls"

STATIC_REDIRECTS = [
    os.path.join(BASE_DIR, "tests/redirects/redirects.csv"),
    os.path.join(BASE_DIR, "tests/redirects/redirects.json"),
]
