from django.conf import settings
import csv
from django.shortcuts import redirect
from urllib.parse import urlparse
from typing import NamedTuple
from django.forms.fields import BooleanField

class RedirectDestination(NamedTuple):
    destination: str
    is_permanent: bool

class StaticRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.data = {}
        for file in settings.STATIC_REDIRECT_FILES:
            with open(file, 'r') as f:
                for row in csv.reader(f):
                    try:
                        is_permanent = BooleanField().to_python(row[2])
                    except IndexError:
                        is_permanent = False

                    self.data[row[0]] = RedirectDestination(row[1], is_permanent)

    def __call__(self, request):
        path = request.get_full_path()

        if destination := self.data.get(path):
            return redirect(destination.destination, permanent=destination.is_permanent)

        elif destination := self.data.get(urlparse(path).path):
            return redirect(destination.destination, permanent=destination.is_permanent)

        return self.get_response(request)
