import csv
import json
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, MiddlewareNotUsed
from django.forms.fields import BooleanField
from django.shortcuts import redirect


class RedirectDestination(NamedTuple):
    destination: str
    is_permanent: bool


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


class StaticRedirectsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.data = {}

        # HACK: Use this to cast to booleans
        boolean_field = BooleanField()

        for file in settings.STATIC_REDIRECTS:
            if not isinstance(file, Path):
                file = Path(file)

            with file.open(mode="r") as f:
                if file.suffix == ".csv":
                    for row in csv.reader(f):
                        try:
                            is_permanent = boolean_field.to_python(row[2])
                        except IndexError:
                            is_permanent = False

                        self.data[normalise_path(row[0])] = RedirectDestination(
                            row[1], is_permanent
                        )

                elif file.suffix == ".json":
                    for entry in json.load(f):
                        self.data[normalise_path(entry["source"])] = (
                            RedirectDestination(
                                entry["destination"], entry.get("is_permanent", False)
                            )
                        )
                else:
                    raise ImproperlyConfigured(f"Unknown file format: {file}")

        if not self.data:
            raise MiddlewareNotUsed()

    def __call__(self, request):
        path = normalise_path(request.get_full_path())

        if destination := self.data.get(path):
            return redirect(destination.destination, permanent=destination.is_permanent)

        path_without_query = urlparse(path).path
        if path != path_without_query and (
            destination := self.data.get(path_without_query)
        ):
            return redirect(destination.destination, permanent=destination.is_permanent)

        return self.get_response(request)
