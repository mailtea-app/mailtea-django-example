import json

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from mailtea import MailteaError

from .forms import NotificationForm
from .mailer import send_notification


def send_form(request: HttpRequest) -> HttpResponse:
    """GET shows the form; POST sends the email and reports what happened."""
    form = NotificationForm(request.POST) if request.method == "POST" else NotificationForm()
    email_id = None
    error = None

    if request.method == "POST" and form.is_valid():
        try:
            email_id = send_notification(**form.cleaned_data)
        except MailteaError as exc:
            # The API's own message names the field it rejected, so show it
            # rather than a generic failure.
            error = exc.message
        else:
            form = NotificationForm()

    return render(
        request,
        "notify/send.html",
        {"form": form, "email_id": email_id, "error": error},
    )


@csrf_exempt  # Called by scripts and agents, not browsers; add your own auth.
@require_POST
def send_api(request: HttpRequest) -> JsonResponse:
    """POST {"to", "subject", "message"} -> {"id": "txemail_..."}."""
    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        payload = None
    if not isinstance(payload, dict):
        return JsonResponse({"error": "Body must be a JSON object."}, status=400)

    form = NotificationForm(payload)
    if not form.is_valid():
        return JsonResponse({"error": "Invalid request.", "details": form.errors}, status=400)

    try:
        email_id = send_notification(**form.cleaned_data)
    except MailteaError as exc:
        # Pass Mailtea's status through so callers can tell "your payload is
        # wrong" from "retry this". status is 0 for client-side errors.
        return JsonResponse({"error": exc.message}, status=exc.status or 502)

    return JsonResponse({"id": email_id})
