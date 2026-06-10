from scraping.schema import FIELDS, Listing
from scraping.scrape_mubawab import parse_location


def test_canonical_schema_contains_model_enrichment_fields() -> None:
    expected = {
        "transaction_type",
        "city",
        "neighborhood",
        "latitude",
        "longitude",
        "floor",
        "property_condition",
        "construction_year",
        "elevator",
        "parking",
        "terrace",
        "balcony",
        "security",
    }
    assert expected.issubset(FIELDS)
    assert list(Listing.__dataclass_fields__) == FIELDS


def test_mubawab_location_is_normalized() -> None:
    assert parse_location("Gauthier, Casablanca") == ("Gauthier", "Casablanca")
    assert parse_location("Rabat") == (None, "Rabat")
