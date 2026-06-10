from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage


AGENT_DIR = Path(__file__).resolve().parents[1] / "AI-Agent"
sys.path.insert(0, str(AGENT_DIR))

import agent as agent_module
from tools import (
    compare_properties,
    detect_listing_price_anomaly,
    find_comparable_properties,
    get_market_summary,
    predict_property_price,
    recommend_properties,
    run_property_scraper,
    search_live_properties,
)


PROPERTY = {
    "surface_m2": 100,
    "rooms": 3,
    "bedrooms": 2,
    "bathrooms": 2,
    "city": "Casablanca",
    "neighborhood": "Maarif",
    "furnished": "NO",
}


def test_all_tool_outputs() -> None:
    prediction = json.loads(predict_property_price.invoke(PROPERTY))
    comparables = json.loads(find_comparable_properties.invoke({**PROPERTY, "limit": 3}))
    anomaly = json.loads(
        detect_listing_price_anomaly.invoke({**PROPERTY, "advertised_price_mad": 5_000_000})
    )
    summary = json.loads(get_market_summary.invoke({"city": "Casablanca"}))
    comparison = json.loads(
        compare_properties.invoke(
            {
                "listings_json": json.dumps(
                    [
                        {"name": "A", "advertised_price_mad": 1_500_000, **PROPERTY},
                        {"name": "B", "advertised_price_mad": 3_000_000, **PROPERTY},
                    ]
                ),
                "budget_mad": 2_000_000,
                "preferred_city": "Casablanca",
            }
        )
    )
    recommendations = json.loads(
        recommend_properties.invoke(
            {"budget_mad": 2_000_000, "city": "Casablanca", "limit": 3}
        )
    )
    assert prediction["estimated_price_mad"] > 0
    assert len(comparables) == 3 and all(item["url"] for item in comparables)
    assert anomaly["classification"]
    assert summary["listing_count"] > 0
    assert comparison[0]["rank"] == 1
    assert len(recommendations) == 3


class FakeBoundModel:
    def __init__(self) -> None:
        self.calls = 0

    def invoke(self, messages: list[object]) -> AIMessage:
        self.calls += 1
        if self.calls == 1:
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_market_summary",
                        "args": {"city": "Casablanca"},
                        "id": "call-1",
                    }
                ],
            )
        assert any(getattr(message, "tool_call_id", None) == "call-1" for message in messages)
        return AIMessage(content="Analyse Casablanca terminee.")


class FakeMistral:
    def __init__(self, **_: object) -> None:
        self.bound = FakeBoundModel()

    def bind_tools(self, _: list[object]) -> FakeBoundModel:
        return self.bound


def test_agent_tool_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key")
    monkeypatch.setattr(agent_module, "ChatMistralAI", FakeMistral)
    result = agent_module.RealEstateAgent().chat("Resume Casablanca.")
    assert "Casablanca" in result


def test_live_search_tool(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "tools.search_properties",
        lambda **_: [
            {
                "title": "Annonce test",
                "url": "https://www.mubawab.ma/fr/a/1",
                "source": "Mubawab",
                "snippet": "Appartement",
                "price_mad": 1_000_000,
                "location": "Casablanca",
                "checked_at": "2026-06-10T00:00:00+00:00",
                "verified": True,
                "status_code": 200,
            }
        ],
    )
    result = json.loads(
        search_live_properties.invoke({"city": "Casablanca", "max_results": 4})
    )
    assert result[0]["verified"] is True
    assert result[0]["source"] == "Mubawab"


def test_scraper_tool(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "tools.run_scraper",
        lambda **kwargs: {"success": True, "source": kwargs["source"]},
    )
    result = json.loads(
        run_property_scraper.invoke(
            {"source": "mubawab", "transaction": "rent", "min_listings": 5}
        )
    )
    assert result == {"success": True, "source": "mubawab"}
