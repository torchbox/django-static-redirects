from django.dispatch import receiver
from django.utils.autoreload import autoreload_started

from .utils import get_redirect_files


@receiver(autoreload_started)
def watch_redirect_files(sender, **kwargs):
    for redirect_file in get_redirect_files():
        sender.watch_dir(redirect_file.parent, redirect_file.name)
