import csv
import json
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class Redirect(NamedTuple):
    source: str
    destination: str
    is_permanent: bool


VALID_EXTENSIONS = {".json", ".csv"}


def get_redirect_files():
    files = []
    for file in getattr(settings, "STATIC_REDIRECTS", []):
        if not isinstance(file, Path):
            file = Path(file)

        if file.suffix not in VALID_EXTENSIONS:
            raise ImproperlyConfigured(f"Unknown file format: {file}")

        files.append(file)

    return files


def normalise_path(url):
    """
    Borrowed from `wagtail.contrib.redirects`.
    """
    # Strip whitespace
    url = url.strip()

    # Parse url
    url_parsed = urlparse(url)

    # Path must start with / but not end with /
    path = url_parsed[2]
    if not path.startswith("/"):
        path = "/" + path

    if path.endswith("/") and len(path) > 1:
        path = path[:-1]

    # Parameters must be sorted alphabetically
    parameters = url_parsed[3]
    parameters_components = parameters.split(";")
    parameters = ";".join(sorted(parameters_components))

    # Query string components must be sorted alphabetically
    query_string = url_parsed[4]
    query_string_components = query_string.split("&")
    query_string = "&".join(sorted(query_string_components))

    if parameters:
        path = path + ";" + parameters

    # Add query string to path
    if query_string:
        path = path + "?" + query_string

    return path


def str_to_bool(value):
    """
    Convert a string to a boolean.

    Copied from `django.forms.fields.BooleanField.to_python`.
    """
    if isinstance(value, str) and value.lower() in ("false", "0"):
        return False
    return bool(value)


def get_redirects():
    """
    Get the raw redirects as configured in Django.
    """
    for file in get_redirect_files():
        with file.open(mode="r") as f:
            if file.suffix == ".csv":
                for row in csv.reader(f):
                    try:
                        is_permanent = str_to_bool(row[2])
                    except IndexError:
                        is_permanent = False

                    yield Redirect(normalise_path(row[0]), row[1], is_permanent)

            elif file.suffix == ".json":
                for entry in json.load(f):
                    yield Redirect(
                        normalise_path(entry["source"]),
                        entry["destination"],
                        entry.get("is_permanent", False),
                    )
