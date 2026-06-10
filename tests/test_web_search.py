from __future__ import annotations

from real_estate import web_search


class FakeDDGS:
    def __init__(self, **_: object) -> None:
        pass

    def __enter__(self) -> "FakeDDGS":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def text(self, *_: object, **__: object) -> list[dict[str, str]]:
        return [
            {
                "title": "Appartement Casablanca 1 500 000 DH",
                "href": "https://www.mubawab.ma/fr/a/123",
                "body": "Appartement a vendre a Maarif",
            },
            {
                "title": "Duplicate",
                "href": "https://www.mubawab.ma/fr/a/123#photos",
                "body": "Meme annonce",
            },
            {
                "title": "Appartement Sarouty",
                "href": "https://www.sarouty.ma/property/456/",
                "body": "Prix 1700000 MAD Casablanca",
            },
            {
                "title": "Domaine interdit",
                "href": "https://example.com/property/789",
                "body": "Ne doit pas apparaitre",
            },
        ]


def test_search_filters_deduplicates_and_verifies(monkeypatch) -> None:
    monkeypatch.setattr(web_search, "DDGS", FakeDDGS)
    monkeypatch.setattr(
        web_search,
        "verify_result",
        lambda url: (url.startswith("https://www.mubawab.ma"), 200, "1 500 000 DH"),
    )

    results = web_search.search_properties(
        city="Casablanca",
        max_results=10,
        verify=True,
    )

    assert len(results) == 2
    assert {item["source"] for item in results} == {"Mubawab", "Sarouty"}
    assert len({item["url"] for item in results}) == 2
    mubawab = next(item for item in results if item["source"] == "Mubawab")
    sarouty = next(item for item in results if item["source"] == "Sarouty")
    assert mubawab["verified"] is True
    assert mubawab["price_mad"] == 1_500_000
    assert sarouty["verified"] is False


def test_allowed_source_rejects_lookalike_domains() -> None:
    assert web_search.allowed_source("https://www.mubawab.ma/fr/a/1") == "Mubawab"
    assert web_search.allowed_source("https://mubawab.ma.evil.example/a/1") is None
