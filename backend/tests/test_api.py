from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_routes():
    response = client.get("/api/routes")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) > 0
    assert "origin" in payload[0]
    assert "destination" in payload[0]


def test_get_taxi_ranks():
    response = client.get("/api/taxi-ranks")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) > 0
    assert "latitude" in payload[0]
    assert "longitude" in payload[0]


def test_association_login():
    response = client.post(
        "/api/auth/association/login",
        json={"email": "admin@gmail.com", "password": "admin123"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "Login successful"
    assert payload["association"]["email"] == "admin@gmail.com"


def test_create_booking():
    booking = {
        "sender_name": "Alice",
        "sender_phone": "08100000000",
        "sender_email": "alice@example.com",
        "receiver_name": "Bob",
        "receiver_phone": "08200000000",
        "receiver_email": "bob@example.com",
        "route_id": 1,
        "package_description": "Books",
        "package_weight_kg": 8,
        "estimated_pickup_time": "2026-09-17T08:30:00",
        "pickup_rank_id": 1,
    }
    response = client.post("/api/bookings", json=booking)
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "pending"
    assert payload["ticket_number"].startswith("TF-")


def test_update_booking_status():
    response = client.get("/api/bookings")
    assert response.status_code == 200
    bookings = response.json()
    assert len(bookings) > 0
    booking_id = bookings[0]["id"]

    response = client.patch(f"/api/bookings/{booking_id}/status", json={"status": "in_transit"})
    assert response.status_code == 200
    assert response.json()["status"] == "in_transit"
