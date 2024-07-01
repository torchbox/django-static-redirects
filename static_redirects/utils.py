import csv
import json
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urlsplit

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
    url_parsed = urlsplit(url)

    # Path must start with / but not end with /
    path = url_parsed.path
    if not path.startswith("/"):
        path = "/" + path

    if path.endswith("/") and len(path) > 1:
        path = path[:-1]

    # Query string components must be sorted alphabetically
    query_string = url_parsed.query
    query_string_components = query_string.split("&")
    query_string = "&".join(sorted(query_string_components))

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
                data = csv.DictReader(f)
            elif file.suffix == ".json":
                data = json.load(f)
            else:
                raise ValueError(f"Unknown file {file}.")

            for entry in data:
                source = entry["source"]

                permanent = entry.get("permanent", False)
                if isinstance(permanent, str):
                    permanent = str_to_bool(permanent)

                if source.startswith("/"):
                    source = (entry.get("host") or "") + normalise_path(source)
                else:
                    source = normalise_path(source)

                yield Redirect(
                    source,
                    entry["destination"],
                    permanent,
                )
