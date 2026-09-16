from __future__ import annotations

from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import API_BASE_URL, APP_NAME, ASSOCIATION_EMAIL, ASSOCIATION_PASSWORD, FRONTEND_BASE_URL
from app.database import Base, SessionLocal, engine, get_db
from app.models import Association, Booking, Route, TaxiRank
from app.schemas import (
    AssociationCreateSchema,
    AssociationLoginSchema,
    BookingCreateSchema,
    BookingSchema,
    RouteSchema,
    TaxiRankSchema,
)
from app.services import hash_password, verify_password
from app.notifications import send_booking_confirmation

app = FastAPI(title=APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_BASE_URL.rstrip("/"),
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def migrate_booking_email_column() -> None:
    with engine.begin() as connection:
        columns = connection.exec_driver_sql("PRAGMA table_info(bookings)").fetchall()
        if not any(column[1] == "sender_email" for column in columns):
            connection.exec_driver_sql("ALTER TABLE bookings ADD COLUMN sender_email VARCHAR(254)")
        if not any(column[1] == "receiver_email" for column in columns):
            connection.exec_driver_sql("ALTER TABLE bookings ADD COLUMN receiver_email VARCHAR(254)")


migrate_booking_email_column()

SEED_ROUTES = [
    Route(
        id=1,
        origin="Prinsloo Taxi Rank",
        destination="Marble Hall Taxi Rank",
        estimated_travel_minutes=120,
        operating_hours="08:00 - 16:30",
        fare=120.0,
    ),
    Route(
        id=2,
        origin="Pretoria Central Taxi Rank",
        destination="Polokwane Rank",
        estimated_travel_minutes=210,
        operating_hours="06:00 - 18:00",
        fare=180.0,
    ),
]

SEED_TAXI_RANKS = [
    TaxiRank(id=1, name="Prinsloo Taxi Rank", city="Pretoria", latitude=-25.7449, longitude=28.1881, operating_hours="08:00 - 16:30"),
    TaxiRank(id=2, name="Marble Hall Taxi Rank", city="Marble Hall", latitude=-24.9667, longitude=29.2878, operating_hours="07:30 - 17:00"),
    TaxiRank(id=3, name="Pretoria Central Taxi Rank", city="Pretoria", latitude=-25.7464, longitude=28.1886, operating_hours="06:00 - 18:00"),
    TaxiRank(id=4, name="Polokwane Rank", city="Polokwane", latitude=-23.8962, longitude=29.4486, operating_hours="05:30 - 18:00"),
]


def seed_default_data() -> None:
    db = SessionLocal()
    try:
        if db.query(Route).count() == 0:
            db.add_all(SEED_ROUTES)
        if db.query(TaxiRank).count() == 0:
            db.add_all(SEED_TAXI_RANKS)
        if db.query(Association).filter_by(email=ASSOCIATION_EMAIL).first() is None:
            db.add(
                Association(
                    name="TripForge Admin",
                    email=ASSOCIATION_EMAIL,
                    password_hash=hash_password(ASSOCIATION_PASSWORD),
                    is_active=True,
                )
            )
        db.commit()
    finally:
        db.close()


seed_default_data()


@app.on_event("startup")
def startup_event() -> None:
    seed_default_data()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "api_base_url": API_BASE_URL}


@app.get("/api/routes", response_model=List[RouteSchema])
def get_routes(db: Session = Depends(get_db)) -> List[Route]:
    try:
        return db.query(Route).all()
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Failed to load routes: {exc}") from exc


@app.get("/api/taxi-ranks", response_model=List[TaxiRankSchema])
def get_taxi_ranks(db: Session = Depends(get_db)) -> List[TaxiRank]:
    try:
        return db.query(TaxiRank).order_by(TaxiRank.name).all()
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Failed to load taxi ranks: {exc}") from exc


@app.post("/api/auth/association/login")
def login_association(payload: AssociationLoginSchema, db: Session = Depends(get_db)):
    association = db.query(Association).filter_by(email=payload.email).first()
    if not association or not verify_password(payload.password, association.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "message": "Login successful",
        "association": {
            "id": association.id,
            "name": association.name,
            "email": association.email,
        },
    }


@app.post("/api/auth/association/register")
def register_association(payload: AssociationCreateSchema, db: Session = Depends(get_db)):
    existing = db.query(Association).filter_by(email=payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Association already exists")

    association = Association(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        is_active=True,
    )
    db.add(association)
    db.commit()
    db.refresh(association)

    return {
        "message": "Association registered successfully",
        "association": {"id": association.id, "name": association.name, "email": association.email},
    }


@app.post("/api/bookings", response_model=BookingSchema)
def create_booking(payload: BookingCreateSchema, db: Session = Depends(get_db)) -> Booking:
    route = db.query(Route).filter_by(id=payload.route_id).first()
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")

    if payload.package_weight_kg > 30:
        raise HTTPException(status_code=400, detail="Package must not exceed 30kg")

    last_booking = db.query(Booking).order_by(Booking.id.desc()).first()
    ticket_number = f"TF-{(last_booking.id + 1) if last_booking else 1:05d}"

    booking = Booking(
        ticket_number=ticket_number,
        sender_name=payload.sender_name,
        sender_phone=payload.sender_phone,
        sender_email=payload.sender_email,
        receiver_name=payload.receiver_name,
        receiver_phone=payload.receiver_phone,
        receiver_email=payload.receiver_email,
        route_id=payload.route_id,
        package_description=payload.package_description,
        package_weight_kg=payload.package_weight_kg,
        estimated_pickup_time=payload.estimated_pickup_time,
        pickup_rank_id=payload.pickup_rank_id,
        status="pending",
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)
    send_booking_confirmation(booking, route)
    return booking


@app.get("/api/bookings", response_model=List[BookingSchema])
def list_bookings(db: Session = Depends(get_db)) -> List[Booking]:
    return db.query(Booking).all()


@app.get("/api/bookings/{booking_id}", response_model=BookingSchema)
def get_booking(booking_id: int, db: Session = Depends(get_db)) -> Booking:
    booking = db.query(Booking).filter_by(id=booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@app.patch("/api/bookings/{booking_id}/status", response_model=BookingSchema)
def update_booking_status(booking_id: int, payload: dict, db: Session = Depends(get_db)) -> Booking:
    booking = db.query(Booking).filter_by(id=booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    new_status = payload.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="status is required")

    allowed = {"pending", "accepted", "declined", "received", "in_transit", "delivered", "closed"}
    if new_status not in allowed:
        raise HTTPException(status_code=400, detail="status is not allowed")

    booking.status = new_status
    db.commit()
    db.refresh(booking)
    return booking
