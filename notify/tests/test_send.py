"""Both send paths, end to end, against the bundled mock Mailtea API.

No API key and no network: the mock listens on localhost, answers like the real
API, and records every request it receives.
"""

import json
import os
import socket
from unittest import mock

from django.test import SimpleTestCase, override_settings

from .mock_mailtea import EMAIL_ID, mock_mailtea

FROM = "Mailtea Examples <examples@acme.test>"


def use_mock(server):
    return override_settings(
        MAILTEA_API_KEY="mt_pat_test",
        MAILTEA_API_BASE_URL=server.url,
        MAILTEA_FROM=FROM,
    )


def closed_port_url():
    """A base URL nothing answers on: take a free port, then give it back."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    return f"http://127.0.0.1:{port}"


class SendFormTests(SimpleTestCase):
    def test_posting_the_form_sends_and_shows_the_id(self):
        with mock_mailtea() as server, use_mock(server):
            response = self.client.post(
                "/",
                {
                    "to": "reader@acme.test",
                    "subject": "Hello from Django",
                    "message": "It works.",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, EMAIL_ID)

        sent = server.last
        self.assertEqual(sent["method"], "POST")
        self.assertEqual(sent["path"], "/v1/emails")
        self.assertTrue(sent["authorization"].startswith("Bearer "))
        self.assertEqual(sent["body"]["from"], FROM)
        self.assertEqual(sent["body"]["to"], "reader@acme.test")
        self.assertEqual(sent["body"]["subject"], "Hello from Django")
        self.assertIn("It works.", sent["body"]["html"])
        self.assertEqual(sent["body"]["text"], "It works.")

    def test_the_message_is_escaped_into_the_html(self):
        with mock_mailtea() as server, use_mock(server):
            self.client.post(
                "/",
                {"to": "reader@acme.test", "subject": "Escaping", "message": "<script>x</script>"},
            )

        html = server.last["body"]["html"]
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_an_invalid_address_never_reaches_mailtea(self):
        with mock_mailtea() as server, use_mock(server):
            response = self.client.post(
                "/", {"to": "not-an-address", "subject": "Nope", "message": "..."}
            )

        self.assertContains(response, "Enter a valid email address")
        self.assertEqual(server.requests, [])

    def test_get_renders_an_empty_form(self):
        response = self.client.get("/")
        self.assertContains(response, 'name="subject"')


class SendApiTests(SimpleTestCase):
    def post_json(self, payload):
        return self.client.post(
            "/api/send", data=json.dumps(payload), content_type="application/json"
        )

    def test_it_returns_the_mailtea_id(self):
        with mock_mailtea() as server, use_mock(server):
            response = self.post_json(
                {"to": "reader@acme.test", "subject": "API send", "message": "Hi there."}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": EMAIL_ID})

        sent = server.last
        self.assertEqual(sent["method"], "POST")
        self.assertEqual(sent["path"], "/v1/emails")
        self.assertEqual(sent["authorization"], "Bearer mt_pat_test")
        self.assertEqual(sent["body"]["subject"], "API send")

    def test_a_bad_payload_is_rejected_before_sending(self):
        with mock_mailtea() as server, use_mock(server):
            response = self.post_json({"to": "reader@acme.test"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("subject", response.json()["details"])
        self.assertEqual(server.requests, [])

    def test_a_mailtea_error_surfaces_instead_of_a_500(self):
        # Nothing configured anywhere, which is how this usually fails in real
        # life. The SDK raises MailteaError before opening a connection, and the
        # view turns it into JSON rather than an unhandled 500.
        no_env = mock.patch.dict(os.environ, {"MAILTEA_API_KEY": "", "MAILTEA_API_BASE_URL": ""})
        with no_env, override_settings(MAILTEA_API_KEY="", MAILTEA_API_BASE_URL=None):
            response = self.post_json(
                {"to": "reader@acme.test", "subject": "No key", "message": "..."}
            )

        self.assertEqual(response.status_code, 502)
        self.assertIn("API key", response.json()["error"])

    def test_an_unreachable_api_surfaces_instead_of_a_500(self):
        # An outage, a DNS failure, or a dropped connection reaches the SDK as
        # an OSError, not a MailteaError. A JSON endpoint that answered it with
        # Django's HTML debug page would be worse than useless to its caller.
        with override_settings(
            MAILTEA_API_KEY="mt_pat_test",
            MAILTEA_API_BASE_URL=closed_port_url(),
            MAILTEA_FROM=FROM,
        ):
            response = self.post_json(
                {"to": "reader@acme.test", "subject": "Outage", "message": "..."}
            )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response["content-type"], "application/json")
        self.assertIn("Could not reach", response.json()["error"])
