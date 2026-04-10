import json
from urllib import error, request

from django.conf import settings


class FlutterwaveGatewayError(Exception):
    pass


def _headers():
    if not settings.FLW_SECRET_KEY:
        raise FlutterwaveGatewayError("Flutterwave secret key is missing.")
    return {
        "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def initialize_payment(*, amount, customer_email, customer_name, tx_ref, metadata):
    payload = {
        "tx_ref": tx_ref,
        "amount": str(amount),
        "currency": "GHS",
        "redirect_url": settings.FLW_REDIRECT_URL,
        "payment_options": "card,mobilemoneyghana",
        "customer": {"email": customer_email or "no-reply@servora.local", "name": customer_name},
        "customizations": {"title": "Servora Booking Payment", "description": "Direct payment to provider"},
        "meta": metadata,
    }
    req = request.Request(
        f"{settings.FLW_BASE_URL}/payments",
        data=json.dumps(payload).encode("utf-8"),
        headers=_headers(),
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise FlutterwaveGatewayError(f"Flutterwave initialize failed: {exc.code}") from exc
    except error.URLError as exc:
        raise FlutterwaveGatewayError("Flutterwave initialize request failed.") from exc

    if body.get("status") != "success":
        raise FlutterwaveGatewayError(body.get("message") or "Flutterwave initialize rejected.")
    return body.get("data", {})


def verify_payment(transaction_id):
    req = request.Request(
        f"{settings.FLW_BASE_URL}/transactions/{transaction_id}/verify",
        headers=_headers(),
        method="GET",
    )
    try:
        with request.urlopen(req, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise FlutterwaveGatewayError(f"Flutterwave verification failed: {exc.code}") from exc
    except error.URLError as exc:
        raise FlutterwaveGatewayError("Flutterwave verification request failed.") from exc

    if body.get("status") != "success":
        raise FlutterwaveGatewayError(body.get("message") or "Flutterwave verification rejected.")
    return body.get("data", {})
