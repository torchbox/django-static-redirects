from collections import Counter

from django.core.checks import Warning, register
from django.utils.text import get_text_list

from .utils import get_redirects


@register("files")
def duplicate_redirects_check(app_configs, **kwargs):
    redirect_sources = []

    for redirect in get_redirects():
        redirect_sources.append(redirect.source)

    duplicate_sources = [k for k, v in Counter(redirect_sources).items() if v > 1]

    if duplicate_sources:
        yield Warning(
            "Static redirect sources must be unique",
            hint="Some redirect sources are duplicated: "
            + get_text_list(sorted(duplicate_sources)),
            id="static_redirects.W001",
        )
