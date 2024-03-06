from django.test import SimpleTestCase


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
