# Mailtea + Django Example

This example shows how to use [Mailtea](https://mailtea.app) with Django to send
an email from a form view and from a JSON endpoint.

## Prerequisites

To get the most out of this guide, you'll need to:

- [Create an API key](https://studio.mailtea.app/api-keys)
- [Verify your domain](https://docs.mailtea.app/docs/documentation/domains)

## Instructions

1. Install dependencies:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and add your API key:
   ```bash
   cp .env.example .env
   ```
   Set `MAILTEA_FROM` to an address on a domain you have verified.
3. Run it:
   ```bash
   python manage.py runserver
   ```
   Open http://127.0.0.1:8000 and send yourself an email, or post to the JSON
   endpoint:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/send \
     -H 'content-type: application/json' \
     -d '{"to":"you@yourdomain.com","subject":"Hello","message":"Sent from Django."}'
   ```

## What this example covers

- Reading `MAILTEA_API_KEY` from the environment in `config/settings.py`, and
  `MAILTEA_API_BASE_URL` for local dev or a self-hosted Mailtea
- Sending with the Python SDK (`mailtea.emails.send`) from an HTML form view
- The same send from a JSON endpoint that returns the Mailtea email id
- Rendering the HTML body from a Django template, so user input is escaped
- Handling failures on both paths: whether the API rejected the email or is
  unreachable, the caller gets the reason (and a 502 from the JSON endpoint)
  rather than an unhandled 500

## Tests

```bash
python manage.py test
```

The tests run against a bundled mock Mailtea server, so they need no API key
and make no network calls.

## Learn more

- [Documentation](https://docs.mailtea.app)
- [API reference](https://docs.mailtea.app/docs/api-reference)
- [Node.js SDK](https://github.com/mailtea-app/mailtea-node) ·
  [Python SDK](https://github.com/mailtea-app/mailtea-python) ·
  [MCP server](https://github.com/mailtea-app/mailtea-mcp)
