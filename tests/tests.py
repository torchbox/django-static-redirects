import os
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings

from static_redirects.utils import get_redirect_files, normalise_path, str_to_bool


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


class GetRedirectsTestCase(SimpleTestCase):
    def test_unknown_file_type(self):
        with override_settings(STATIC_REDIRECTS=[Path(__file__)]):
            with self.assertRaises(ImproperlyConfigured):
                get_redirect_files()


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


class NormalisePathTestCase(SimpleTestCase):
    def setUp(self):
        self.path = normalise_path(
            "/Hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2"
        )

    def test_valid_path_noop(self):
        self.assertEqual(normalise_path(self.path), self.path)

    def test_path_normalisation(self):
        self.assertEqual(
            normalise_path(  # The exact same URL
                "/Hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2"
            ),
            self.path,
        )
        self.assertEqual(
            normalise_path(  # Scheme, hostname and port ignored
                "http://mywebsite.com:8000/Hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2"
            ),
            self.path,
        )
        self.assertEqual(
            normalise_path(  # Leading slash can be omitted
                "Hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2"
            ),
            self.path,
        )
        self.assertEqual(
            normalise_path(  # Trailing slashes are ignored
                "Hello/world.html/;fizz=three;buzz=five?foo=Bar&Baz=quux2"
            ),
            self.path,
        )
        self.assertEqual(
            normalise_path(  # Fragments are ignored
                "/Hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2#cool"
            ),
            self.path,
        )
        self.assertEqual(
            normalise_path(  # Order of query string parameters is ignored
                "/Hello/world.html;fizz=three;buzz=five?Baz=quux2&foo=Bar"
            ),
            self.path,
        )
        self.assertEqual(
            normalise_path(  # Order of parameters is ignored
                "/Hello/world.html;buzz=five;fizz=three?foo=Bar&Baz=quux2"
            ),
            self.path,
        )
        self.assertEqual(
            normalise_path(  # Leading whitespace
                "  /Hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2"
            ),
            self.path,
        )
        self.assertEqual(
            normalise_path(  # Trailing whitespace
                "/Hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2  "
            ),
            self.path,
        )

    def test_normalise_different_paths(self):
        self.assertNotEqual(
            normalise_path(  # 'hello' is lowercase
                "/hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2"
            ),
            self.path,
        )
        self.assertNotEqual(
            normalise_path(  # No '.html'
                "/Hello/world;fizz=three;buzz=five?foo=Bar&Baz=quux2"
            ),
            self.path,
        )
        self.assertNotEqual(
            normalise_path(  # Query string parameter value has wrong case
                "/Hello/world.html;fizz=three;buzz=five?foo=bar&Baz=Quux2"
            ),
            self.path,
        )
        self.assertNotEqual(
            normalise_path(  # Query string parameter name has wrong case
                "/Hello/world.html;fizz=three;buzz=five?foo=Bar&baz=quux2"
            ),
            self.path,
        )
        self.assertNotEqual(
            normalise_path(  # Parameter value has wrong case
                "/Hello/world.html;fizz=three;buzz=Five?foo=Bar&Baz=quux2"
            ),
            self.path,
        )
        self.assertNotEqual(
            normalise_path(  # Parameter name has wrong case
                "/Hello/world.html;Fizz=three;buzz=five?foo=Bar&Baz=quux2"
            ),
            self.path,
        )
        self.assertNotEqual(
            normalise_path("/Hello/world.html?foo=Bar&Baz=quux2"),  # Missing params
            self.path,
        )
        self.assertNotEqual(
            normalise_path(  # 'WORLD' is uppercase
                "/Hello/WORLD.html;fizz=three;buzz=five?foo=Bar&Baz=quux2"
            ),
            self.path,
        )
        self.assertNotEqual(
            normalise_path(  # '.htm' is not the same as '.html'
                "/Hello/world.htm;fizz=three;buzz=five?foo=Bar&Baz=quux2"
            ),
            self.path,
        )

        self.assertEqual("/", normalise_path("/"))  # '/' should stay '/'

    def test_doesnt_crash_on_garbage_data(self):
        normalise_path("This is not a URL")
        normalise_path("//////hello/world")
        normalise_path("!#@%$*")
        normalise_path("C:\\Program Files (x86)\\Some random program\\file.txt")

    def test_unicode_path_normalisation(self):
        self.assertEqual(
            "/here/tésting-ünicode",  # stays the same
            normalise_path("/here/tésting-ünicode"),
        )

        self.assertNotEqual(  # Doesn't remove unicode characters
            "/here/testing-unicode", normalise_path("/here/tésting-ünicode")
        )


class StrToBoolTestCase(SimpleTestCase):
    def test_str_to_true(self):
        self.assertTrue(str_to_bool("true"))
        self.assertTrue(str_to_bool("True"))
        self.assertTrue(str_to_bool("1"))

    def test_str_to_false(self):
        self.assertFalse(str_to_bool("false"))
        self.assertFalse(str_to_bool("False"))
        self.assertFalse(str_to_bool("0"))
