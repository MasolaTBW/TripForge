from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import RESEND_API_KEY, RESEND_FROM_EMAIL
from app.models import Booking, Route


def send_booking_confirmation(booking: Booking, route: Route) -> str:
    if not RESEND_API_KEY:
        return "not_configured"

    payload = {
        "from": RESEND_FROM_EMAIL,
        "to": [booking.sender_email, booking.receiver_email],
        "subject": f"TripForge booking confirmation: {booking.ticket_number}",
        "text": (
            f"Your TripForge package booking is confirmed.\n\n"
            f"Ticket: {booking.ticket_number}\n"
            f"Route: {route.origin} to {route.destination}\n"
            f"Pickup time: {booking.estimated_pickup_time}\n"
            f"Package: {booking.package_description}\n"
            f"Estimated weight: {booking.package_weight_kg} kg\n\n"
            "Status: pending"
        ),
    }
    request = Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            return "sent" if 200 <= response.status < 300 else f"failed:{response.status}"
    except (HTTPError, URLError, TimeoutError):
        return "failed"
