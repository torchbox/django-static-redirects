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
        self.assertRedirects(response, "/bar", status_code=301, fetch_redirect_response=False)

    def test_redirect_from_json(self):
        response = self.client.get("/json")
        self.assertRedirects(response, "/json-dest", status_code=301, fetch_redirect_response=False)

    @override_settings(STATIC_REDIRECT_FILES=[])
    def test_no_files(self):
        response = self.client.get("/foo")
        self.assertEqual(response.status_code, 404)
