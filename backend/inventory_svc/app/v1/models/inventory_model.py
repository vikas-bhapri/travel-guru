from sqlalchemy import  Integer, String, Float, ForeignKey, Text, DateTime, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..models.base import Base
from datetime import datetime, timezone

class Destination(Base):
    destination_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[str] = mapped_column(DateTime,default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    hotels = relationship("Hotel", back_populates="destination", cascade="all, delete-orphan")
    packages = relationship("TourPackage", back_populates="destination", cascade="all, delete-orphan")


class Hotel(Base):
    hotel_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('destination.destination_id'), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    rating: Mapped[float] = mapped_column()
    price_per_night: Mapped[float] = mapped_column()
    latitude: Mapped[float] = mapped_column()
    longitude: Mapped[float] = mapped_column()
    created_at: Mapped[str] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[str] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    destination = relationship("Destination", back_populates="hotels")
    rooms = relationship("Room", back_populates="hotel", cascade="all, delete-orphan")
    amentities = relationship("Amenity", secondary="hotel_amenities", back_populates="hotel")
    pricing_rules = relationship("PricingRule", back_populates="hotel", cascade="all, delete-orphan")

class Room(Base):
    room_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hotel_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('hotel.hotel_id'), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    capacity_adults: Mapped[int] = mapped_column(nullable=False)
    capacity_children: Mapped[int] = mapped_column(nullable=False)
    smoking_allowed: Mapped[bool] = mapped_column(nullable=False)
    view: Mapped[str] = mapped_column()
    created_at: Mapped[str] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[str] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    hotel = relationship("Hotel", back_populates="rooms")
    availability = relationship("RoomAvailability", back_populates="room", cascade="all, delete-orphan")

class Amenity(Base):
    amenity_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column()
    icon_url: Mapped[str] = mapped_column()
    created_at: Mapped[str] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[str] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    hotels = relationship("Hotel", secondary="hotel_amenities", back_populates="amenity")

class HotelAmenity(Base):
    hotel_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('hotel.hotel_id'), primary_key=True)
    amenity_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('amenity.amenity_id'), primary_key=True)

class Flight(Base):
    flight_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    airline: Mapped[str] = mapped_column(nullable=False)
    origin: Mapped[str] = mapped_column(nullable=False)
    destination: Mapped[str] = mapped_column(nullable=False)
    departure_time: Mapped[str] = mapped_column(DateTime, nullable=False)
    arrival_time: Mapped[str] = mapped_column(DateTime, nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    cabin_class: Mapped[str] = mapped_column()
    created_at: Mapped[str] = mapped_column(DateTime, default=datetime.now(timezone.utc))

class TourPackage(Base):
    package_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('destination.destination_id'), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(nullable=False)
    duration_days: Mapped[int] = mapped_column(nullable=False)
    theme: Mapped[str] = mapped_column()
    created_at: Mapped[str] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[str] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    destination = relationship("Destination", back_populates="tour_packages")
    itenary_items = relationship("PackageItenaryItem", back_populates="package", cascade="all, delete-orphan")

class PackageItenaryItem(Base):
    item_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('tourpackage.package_id'), nullable=False)
    day_number: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    package = relationship("TourPackage", back_populates="itenary_items")

class RoomAvailability(Base):
    availability_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('room.room_id'), nullable=False)
    date: Mapped[str] = mapped_column(DateTime, nullable=False)
    available_units: Mapped[int] = mapped_column(nullable=False)
    min_stay: Mapped[int] = mapped_column(nullable=False)
    closed_to_arrivals: Mapped[bool] = mapped_column(nullable=False)
    closed_to_departures: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    room = relationship("Room", back_populates="availability")

    __table_args__ = (
        UniqueConstraint('room_id', 'date', name='uq_room_date'),
    )

class RoomRate(Base):
    rate_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('room.room_id'), nullable=False)
    hotel_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('hotel.hotel_id'), nullable=False)
    date: Mapped[str] = mapped_column(DateTime, nullable=False)
    base_price: Mapped[float] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(nullable=False, default='INR')
    refundable: Mapped[bool] = mapped_column(nullable=False)
    meal_plan: Mapped[str] = mapped_column()
    tax_inclusive: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    hotel = relationship("Hotel", back_populates="rate_plans")
    room = relationship("Room", back_populates="rate_plans")

    __table_args__ = (
        UniqueConstraint('room_id', 'date', name='uq_room_rate_date'),
    )

class PricingRule(Base):
    rule_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hotel_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('hotel.hotel_id'), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    rule_type: Mapped[str] = mapped_column(nullable=False)
    percentage: Mapped[float] = mapped_column()
    start_date: Mapped[str] = mapped_column(DateTime,nullable=False)
    end_date: Mapped[str] = mapped_column(DateTime, nullable=False)
    conditions: Mapped[str] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    hotel = relationship("Hotel", back_populates="pricing_rules")

class Media(Base):
    media_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_type: Mapped[str] = mapped_column(nullable=False)
    resource_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    url: Mapped[str] = mapped_column(nullable=False)
    caption: Mapped[str] = mapped_column()
    created_at: Mapped[str] = mapped_column(DateTime, default=datetime.now(timezone.utc))
