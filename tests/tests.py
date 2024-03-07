import os
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings


class RedirectsMiddlewareTestCase(SimpleTestCase):
    def test_redirect(self):
        response = self.client.get("/foo")
        self.assertRedirects(response, "/bar", fetch_redirect_response=False)

    def test_redirect_without_query(self):
        response = self.client.get("/foo?something=else")
        self.assertRedirects(response, "/bar", fetch_redirect_response=False)

    def test_permanent_redirect(self):
        response = self.client.get("/foo-permanent")
        self.assertRedirects(
            response, "/bar", status_code=301, fetch_redirect_response=False
        )

    def test_redirect_from_json(self):
        response = self.client.get("/json")
        self.assertRedirects(
            response, "/json-dest", status_code=301, fetch_redirect_response=False
        )

    @override_settings(STATIC_REDIRECTS=[])
    def test_no_files(self):
        response = self.client.get("/foo")
        self.assertEqual(response.status_code, 404)

    def test_unknown_file_type(self):
        with override_settings(STATIC_REDIRECTS=[Path(__file__)]):
            with self.assertRaises(ImproperlyConfigured):
                self.client.get("/foo")


class DuplicateRedirectsCheckTestCase(SimpleTestCase):
    def run_checks(self):
        stdout = StringIO()
        stderr = StringIO()
        call_command("check", "-t", "files", stdout=stdout, stderr=stderr)
        return stdout.getvalue(), stderr.getvalue()

    def test_passes_by_default(self):
        stdout, stderr = self.run_checks()
        self.assertNotIn("static_redirects.W001", stderr)
        self.assertNotIn("static_redirects.W001", stdout)

    @override_settings(
        STATIC_REDIRECTS=[
            os.path.join(settings.BASE_DIR, "tests/redirects/redirects.csv"),
            os.path.join(settings.BASE_DIR, "tests/redirects/redirects.csv"),
        ]
    )
    def test_reports_duplicates(self):
        stdout, stderr = self.run_checks()
        self.assertIn("static_redirects.W001", stderr)
        self.assertIn("/foo", stderr)
