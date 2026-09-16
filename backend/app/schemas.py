from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class RouteSchema(BaseModel):
    id: int
    origin: str
    destination: str
    estimated_travel_minutes: int
    operating_hours: str
    fare: float


class TaxiRankSchema(BaseModel):
    id: int
    name: str
    city: str
    latitude: float
    longitude: float
    operating_hours: str


class BookingCreateSchema(BaseModel):
    sender_name: str
    sender_phone: str
    sender_email: str
    receiver_name: str
    receiver_phone: str
    receiver_email: str
    route_id: int
    package_description: str
    package_weight_kg: float = Field(..., ge=0.1, le=30)
    estimated_pickup_time: str
    pickup_rank_id: int


class BookingSchema(BaseModel):
    id: int
    ticket_number: str
    sender_name: str
    sender_phone: str
    sender_email: Optional[str] = None
    receiver_name: str
    receiver_phone: str
    receiver_email: Optional[str] = None
    route_id: int
    package_description: str
    package_weight_kg: float
    estimated_pickup_time: str
    pickup_rank_id: int
    status: str = "pending"
    association_response: Optional[str] = None


class AssociationLoginSchema(BaseModel):
    email: str
    password: str


class AssociationCreateSchema(BaseModel):
    name: str
    email: str
    password: str
