from django.conf import settings
import csv
from django.shortcuts import redirect
from typing import NamedTuple
from django.forms.fields import BooleanField
from pathlib import Path
import json
from django.core.exceptions import MiddlewareNotUsed


class RedirectDestination(NamedTuple):
    destination: str
    is_permanent: bool


class StaticRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.data = {}

        # HACK: Use this to cast to booleans
        boolean_field = BooleanField()

        for file in settings.STATIC_REDIRECT_FILES:
            if not isinstance(file, Path):
                file = Path(file)

            with file.open(mode="r") as f:
                if file.suffix == ".csv":
                    for row in csv.reader(f):
                        try:
                            is_permanent = boolean_field.to_python(row[2])
                        except IndexError:
                            is_permanent = False

                        self.data[row[0]] = RedirectDestination(row[1], is_permanent)

                elif file.suffix == ".json":
                    for entry in json.load(f):
                        self.data[entry["source"]] = RedirectDestination(
                            entry["destination"], entry.get("is_permanent", False)
                        )

        if not self.data:
            raise MiddlewareNotUsed()

    def __call__(self, request):
        full_path = request.get_full_path()

        if destination := self.data.get(full_path):
            return redirect(destination.destination, permanent=destination.is_permanent)

        elif full_path != request.path and (destination := self.data.get(request.path)):
            return redirect(destination.destination, permanent=destination.is_permanent)

        return self.get_response(request)
