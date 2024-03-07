from typing import NamedTuple
from urllib.parse import urlparse

from django.core.exceptions import MiddlewareNotUsed
from django.shortcuts import redirect as redirect_response

from .utils import get_redirects, normalise_path


class RedirectDestination(NamedTuple):
    destination: str
    is_permanent: bool


class StaticRedirectsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.data = {}

        for redirect in get_redirects():
            self.data[redirect.source] = RedirectDestination(
                redirect.destination, redirect.is_permanent
            )

        if not self.data:
            raise MiddlewareNotUsed()

    def __call__(self, request):
        path = normalise_path(request.get_full_path())

        if destination := self.data.get(path):
            return redirect_response(
                destination.destination, permanent=destination.is_permanent
            )

        path_without_query = urlparse(path).path
        if path != path_without_query and (
            destination := self.data.get(path_without_query)
        ):
            return redirect_response(
                destination.destination, permanent=destination.is_permanent
            )

        return self.get_response(request)
