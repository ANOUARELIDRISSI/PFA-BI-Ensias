from __future__ import annotations

import pytest

from real_estate.services import ListingInput, PropertyInput, RealEstateService


@pytest.fixture(scope="module")
def service() -> RealEstateService:
    return RealEstateService()


@pytest.fixture()
def apartment() -> PropertyInput:
    return PropertyInput(100, 3, 2, 2, "Casablanca", "Maarif", "NO")


def test_prediction(service: RealEstateService, apartment: PropertyInput) -> None:
    result = service.predict_price(apartment)
    assert result["estimated_price_mad"] > 0
    assert result["indicative_range_mad"][0] <= result["estimated_price_mad"]
    assert result["indicative_range_mad"][1] >= result["estimated_price_mad"]


def test_comparables(service: RealEstateService, apartment: PropertyInput) -> None:
    result = service.find_comparables(apartment, limit=5)
    assert len(result) == 5
    assert all(item["url"] and item["price_per_m2"] > 0 for item in result)


def test_anomaly(service: RealEstateService, apartment: PropertyInput) -> None:
    estimate = service.predict_price(apartment)["estimated_price_mad"]
    result = service.detect_price_anomaly(estimate * 1.5, apartment)
    assert result["classification"] == "potentiellement_surevalue"


def test_market_summary(service: RealEstateService) -> None:
    result = service.market_summary("Casablanca")
    assert result["listing_count"] > 0
    assert result["median_price_per_m2"] > 0


def test_invalid_market(service: RealEstateService) -> None:
    with pytest.raises(ValueError, match="No listings"):
        service.market_summary("Ville Inexistante")


def test_compare_properties_ranks_best_value(
    service: RealEstateService,
    apartment: PropertyInput,
) -> None:
    estimate = service.predict_price(apartment)["estimated_price_mad"]
    listings = [
        ListingInput("Prix correct", estimate, apartment, "https://example.com/a"),
        ListingInput("Tres cher", estimate * 2, apartment, "https://example.com/b"),
    ]
    result = service.compare_properties(
        listings,
        budget_mad=estimate * 1.2,
        preferred_city="Casablanca",
        preferred_neighborhood="Maarif",
        preferred_surface_m2=100,
    )
    assert result[0]["name"] == "Prix correct"
    assert result[0]["score"] > result[1]["score"]
    assert result[0]["rank"] == 1


def test_recommendations_respect_budget_and_city(service: RealEstateService) -> None:
    result = service.recommend_properties(
        budget_mad=2_000_000,
        city="Casablanca",
        min_surface_m2=70,
        min_bedrooms=2,
        limit=5,
    )
    assert result
    assert all(item["price_mad"] <= 2_000_000 for item in result)
    assert all(item["city"].casefold() == "casablanca" for item in result)
    assert [item["rank"] for item in result] == list(range(1, len(result) + 1))
