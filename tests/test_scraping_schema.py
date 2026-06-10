from scraping.schema import FIELDS, Listing


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
