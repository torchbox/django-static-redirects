from django.apps import AppConfig


class StaticRedirectsAppConfig(AppConfig):
    name = "static_redirects"

    def ready(self):
        from . import checks, signal_handlers  # noqa:F401
