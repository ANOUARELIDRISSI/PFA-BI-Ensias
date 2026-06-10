"""Mistral tools backed by the parent project's ML and cleaned data."""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

from langchain_core.tools import tool


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from real_estate.services import ListingInput, PropertyInput, RealEstateService


@lru_cache(maxsize=1)
def get_service() -> RealEstateService:
    return RealEstateService()


def _property(
    surface_m2: float,
    rooms: float,
    bedrooms: float,
    bathrooms: float,
    city: str,
    neighborhood: str,
    furnished: str,
) -> PropertyInput:
    return PropertyInput(
        surface_m2=surface_m2,
        rooms=rooms,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        city=city,
        neighborhood=neighborhood,
        furnished=furnished,
    )


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


@tool
def predict_property_price(
    surface_m2: float,
    rooms: float,
    bedrooms: float,
    bathrooms: float,
    city: str,
    neighborhood: str = "Unknown",
    furnished: str = "NO",
) -> str:
    """Estimer le prix de vente d'un appartement au Maroc en MAD."""
    return _json(
        get_service().predict_price(
            _property(surface_m2, rooms, bedrooms, bathrooms, city, neighborhood, furnished)
        )
    )


@tool
def find_comparable_properties(
    surface_m2: float,
    rooms: float,
    bedrooms: float,
    bathrooms: float,
    city: str,
    neighborhood: str = "Unknown",
    furnished: str = "NO",
    limit: int = 5,
) -> str:
    """Trouver des annonces comparables avec leurs prix et URLs sources."""
    return _json(
        get_service().find_comparables(
            _property(surface_m2, rooms, bedrooms, bathrooms, city, neighborhood, furnished),
            limit=limit,
        )
    )


@tool
def detect_listing_price_anomaly(
    advertised_price_mad: float,
    surface_m2: float,
    rooms: float,
    bedrooms: float,
    bathrooms: float,
    city: str,
    neighborhood: str = "Unknown",
    furnished: str = "NO",
) -> str:
    """Comparer un prix annonce avec l'estimation du modele."""
    return _json(
        get_service().detect_price_anomaly(
            advertised_price_mad,
            _property(surface_m2, rooms, bedrooms, bathrooms, city, neighborhood, furnished),
        )
    )


@tool
def get_market_summary(city: str, neighborhood: str = "") -> str:
    """Resumer les prix et surfaces observes pour une ville ou un quartier."""
    return _json(get_service().market_summary(city, neighborhood or None))


@tool
def compare_properties(
    listings_json: str,
    budget_mad: float = 0,
    preferred_city: str = "",
    preferred_neighborhood: str = "",
    preferred_surface_m2: float = 0,
) -> str:
    """Comparer 2 a 20 biens. listings_json doit etre une liste JSON de biens."""
    raw_listings = json.loads(listings_json)
    listings = []
    for index, item in enumerate(raw_listings, start=1):
        listings.append(
            ListingInput(
                name=item.get("name") or f"Bien {index}",
                advertised_price_mad=float(item["advertised_price_mad"]),
                property=_property(
                    float(item["surface_m2"]),
                    float(item.get("rooms", item.get("bedrooms", 0))),
                    float(item.get("bedrooms", 0)),
                    float(item.get("bathrooms", 0)),
                    item["city"],
                    item.get("neighborhood", "Unknown"),
                    item.get("furnished", "NO"),
                ),
                url=item.get("url", ""),
            )
        )
    return _json(
        get_service().compare_properties(
            listings,
            budget_mad=budget_mad or None,
            preferred_city=preferred_city or None,
            preferred_neighborhood=preferred_neighborhood or None,
            preferred_surface_m2=preferred_surface_m2 or None,
        )
    )


@tool
def recommend_properties(
    budget_mad: float,
    city: str,
    neighborhood: str = "",
    min_surface_m2: float = 0,
    min_bedrooms: float = 0,
    limit: int = 5,
) -> str:
    """Recommander des annonces locales selon un budget et des criteres."""
    return _json(
        get_service().recommend_properties(
            budget_mad=budget_mad,
            city=city,
            neighborhood=neighborhood or None,
            min_surface_m2=min_surface_m2,
            min_bedrooms=min_bedrooms,
            limit=limit,
        )
    )


REAL_ESTATE_TOOLS = [
    predict_property_price,
    find_comparable_properties,
    detect_listing_price_anomaly,
    get_market_summary,
    compare_properties,
    recommend_properties,
]
