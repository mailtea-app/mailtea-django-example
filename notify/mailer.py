"""The one place this example talks to Mailtea."""

from __future__ import annotations

from django.conf import settings
from django.template.loader import render_to_string
from mailtea import Mailtea, MailteaError


def _client() -> Mailtea:
    # Built per send rather than at import time, so the settings stay the single
    # source of truth (and tests can point base_url at a mock server).
    return Mailtea(settings.MAILTEA_API_KEY, base_url=settings.MAILTEA_API_BASE_URL)


def send_notification(*, to: str, subject: str, message: str) -> str:
    """Send one email and return its Mailtea id. Raises ``MailteaError``."""
    # Rendering through a template means Django escapes the message for us,
    # so a recipient's text can never inject markup into the email.
    html = render_to_string("notify/email.html", {"message": message})

    try:
        return _client().emails.send(
            # `from_` because `from` is a Python keyword.
            from_=settings.MAILTEA_FROM,
            to=to,
            subject=subject,
            html=html,
            text=message,
        )["id"]
    except OSError as exc:
        # The SDK raises MailteaError for everything the API answers, but a
        # socket-level failure — DNS, a refused connection, a connection
        # dropped mid-request — arrives as a bare OSError. Both views know how
        # to report a MailteaError, so an outage becomes one here instead of
        # reaching the caller as an unhandled 500.
        raise MailteaError(
            f"Could not reach the Mailtea API: {exc}", code="connection_error"
        ) from exc
