from urllib.parse import urlparse

from django.core.exceptions import MiddlewareNotUsed
from django.shortcuts import redirect as redirect_response

from .utils import get_redirects, normalise_path


class StaticRedirectsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.data = {}

        self.has_hostname_matching = False
        self.has_querystring_matching = False

        for redirect in get_redirects():
            self.data[redirect.source] = redirect

            if not redirect.source.startswith("/"):
                self.has_hostname_matching = True

            if "?" in redirect.source:
                self.has_querystring_matching = True

        if not self.data:
            raise MiddlewareNotUsed()

    def __call__(self, request):
        path = normalise_path(request.get_full_path())

        if destination := self.data.get(path):
            return redirect_response(
                destination.destination, permanent=destination.is_permanent
            )

        if self.has_querystring_matching:
            path_without_query = urlparse(path).path
            if path != path_without_query and (
                destination := self.data.get(path_without_query)
            ):
                return redirect_response(
                    destination.destination, permanent=destination.is_permanent
                )

        if self.has_hostname_matching:
            host = request.get_host()

            if destination := self.data.get(host + path):
                return redirect_response(
                    destination.destination, permanent=destination.is_permanent
                )

            if self.has_querystring_matching and (
                destination := self.data.get(host + path_without_query)
            ):
                return redirect_response(
                    destination.destination, permanent=destination.is_permanent
                )

        return self.get_response(request)
