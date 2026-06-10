"""Canonical schema shared by all real-estate collectors."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Listing:
    source: str
    source_id: str | int | None
    scraped_at: str
    published_at: str | None
    page: int
    transaction_type: str
    property_type: str | None
    title: str | None
    description: str | None
    price: str | None
    price_mad: float | None
    location: str | None
    city: str | None
    neighborhood: str | None
    latitude: float | None
    longitude: float | None
    surface_m2: float | None
    rooms: float | None
    bedrooms: float | None
    bathrooms: float | None
    floor: float | None
    total_floors: float | None
    property_condition: str | None
    construction_year: int | None
    furnished: str | None
    elevator: bool | None
    parking: bool | None
    terrace: bool | None
    balcony: bool | None
    security: bool | None
    url: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


FIELDS = list(Listing.__dataclass_fields__)
