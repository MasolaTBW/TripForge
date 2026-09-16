from __future__ import annotations

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text

from app.database import Base


class Association(Base):
    __tablename__ = "associations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String(150), nullable=False)
    destination = Column(String(150), nullable=False)
    estimated_travel_minutes = Column(Integer, nullable=False)
    operating_hours = Column(String(100), nullable=False)
    fare = Column(Float, nullable=False)


class TaxiRank(Base):
    __tablename__ = "taxi_ranks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    city = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    operating_hours = Column(String(100), nullable=False)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, nullable=False)
    sender_name = Column(String(150), nullable=False)
    sender_phone = Column(String(50), nullable=False)
    sender_email = Column(String(254), nullable=True)
    receiver_name = Column(String(150), nullable=False)
    receiver_phone = Column(String(50), nullable=False)
    receiver_email = Column(String(254), nullable=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    package_description = Column(Text, nullable=False)
    package_weight_kg = Column(Float, nullable=False)
    estimated_pickup_time = Column(String(50), nullable=False)
    pickup_rank_id = Column(Integer, nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    association_response = Column(Text, nullable=True)
