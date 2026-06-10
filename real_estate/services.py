from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import cached_property
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = PROJECT_ROOT / "data/processed/real_estate_clean.csv"
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models/best_price_model.joblib"


@dataclass(frozen=True)
class PropertyInput:
    surface_m2: float
    rooms: float
    bedrooms: float
    bathrooms: float
    city: str
    neighborhood: str = "Unknown"
    furnished: str = "NO"
    source: str = "unknown"
    property_type: str = "Appartement"


@dataclass(frozen=True)
class ListingInput:
    name: str
    advertised_price_mad: float
    property: PropertyInput
    url: str = ""


class RealEstateService:
    """Prediction and analytics over the project's local ML artifacts."""

    def __init__(
        self,
        data_path: Path = DEFAULT_DATA_PATH,
        model_path: Path = DEFAULT_MODEL_PATH,
    ) -> None:
        self.data_path = Path(data_path)
        self.model_path = Path(model_path)

    @cached_property
    def data(self) -> pd.DataFrame:
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Cleaned data not found at {self.data_path}. "
                "Run: uv run python -m ml.clean_data"
            )
        data = pd.read_csv(self.data_path)
        required = {"price_mad", "surface_m2", "city", "neighborhood", "source", "url"}
        missing = required.difference(data.columns)
        if missing:
            raise ValueError(f"Cleaned dataset is missing columns: {sorted(missing)}")
        return data

    @cached_property
    def model(self) -> Any:
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Trained model not found at {self.model_path}. "
                "Run: uv run python -m ml.train"
            )
        return joblib.load(self.model_path)

    @staticmethod
    def _validate_property(item: PropertyInput) -> None:
        if not 10 <= item.surface_m2 <= 1_000:
            raise ValueError("surface_m2 must be between 10 and 1000.")
        for field in ("rooms", "bedrooms", "bathrooms"):
            if not 0 <= getattr(item, field) <= 30:
                raise ValueError(f"{field} must be between 0 and 30.")
        if not item.city.strip():
            raise ValueError("city is required.")

    @staticmethod
    def _frame(item: PropertyInput) -> pd.DataFrame:
        return pd.DataFrame([asdict(item)])

    def predict_price(self, item: PropertyInput) -> dict[str, Any]:
        self._validate_property(item)
        prediction = max(0.0, float(self.model.predict(self._frame(item))[0]))
        comparables = self.find_comparables(item, limit=10)
        prices = [row["price_mad"] for row in comparables]
        if len(prices) >= 3:
            lower = float(np.quantile(prices, 0.25))
            upper = float(np.quantile(prices, 0.75))
        else:
            lower, upper = prediction * 0.8, prediction * 1.2
        return {
            "estimated_price_mad": round(prediction),
            "estimated_price_per_m2": round(prediction / item.surface_m2),
            "indicative_range_mad": [round(min(lower, prediction)), round(max(upper, prediction))],
            "comparable_count": len(prices),
            "warning": (
                "Estimation indicative basee sur un petit jeu de donnees. "
                "Elle ne remplace pas une expertise immobiliere."
            ),
        }

    def find_comparables(self, item: PropertyInput, limit: int = 5) -> list[dict[str, Any]]:
        self._validate_property(item)
        if not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50.")
        data = self.data.copy()
        candidates = data[data["city"].str.casefold() == item.city.strip().casefold()].copy()
        if candidates.empty:
            candidates = data.copy()
        neighborhood = item.neighborhood.strip().casefold()
        candidates["same_neighborhood"] = (
            candidates["neighborhood"].fillna("").str.casefold() == neighborhood
        ).astype(int)
        candidates["surface_difference"] = (candidates["surface_m2"] - item.surface_m2).abs()
        candidates["room_difference"] = (
            candidates["rooms"].fillna(item.rooms) - item.rooms
        ).abs()
        candidates["similarity_score"] = (
            candidates["same_neighborhood"] * 100
            - candidates["surface_difference"]
            - candidates["room_difference"] * 10
        )
        selected = candidates.sort_values(
            ["similarity_score", "surface_difference"], ascending=[False, True]
        ).head(limit)
        fields = [
            "source", "title", "price_mad", "surface_m2", "rooms", "bedrooms",
            "bathrooms", "city", "neighborhood", "url",
        ]
        records = selected[fields].replace({np.nan: None}).to_dict(orient="records")
        for record in records:
            record["price_per_m2"] = round(record["price_mad"] / record["surface_m2"])
        return records

    def detect_price_anomaly(
        self,
        advertised_price_mad: float,
        item: PropertyInput,
        threshold: float = 0.2,
    ) -> dict[str, Any]:
        if advertised_price_mad <= 0:
            raise ValueError("advertised_price_mad must be positive.")
        estimate = self.predict_price(item)
        predicted = float(estimate["estimated_price_mad"])
        difference = advertised_price_mad - predicted
        ratio = difference / predicted if predicted else 0.0
        if ratio > threshold:
            classification = "potentiellement_surevalue"
        elif ratio < -threshold:
            classification = "potentiellement_sous_evalue"
        else:
            classification = "dans_la_fourchette"
        return {
            "classification": classification,
            "advertised_price_mad": round(advertised_price_mad),
            "estimated_price_mad": round(predicted),
            "difference_mad": round(difference),
            "difference_percent": round(ratio * 100, 1),
            "warning": "Un ecart de prix ne prouve ni une fraude ni une bonne affaire.",
        }

    def market_summary(
        self,
        city: str | None = None,
        neighborhood: str | None = None,
    ) -> dict[str, Any]:
        data = self.data.copy()
        if city:
            data = data[data["city"].str.casefold() == city.strip().casefold()]
        if neighborhood:
            data = data[
                data["neighborhood"].fillna("").str.casefold()
                == neighborhood.strip().casefold()
            ]
        if data.empty:
            raise ValueError("No listings match the requested market.")
        price_per_m2 = data["price_mad"] / data["surface_m2"]
        return {
            "city": city,
            "neighborhood": neighborhood,
            "listing_count": int(len(data)),
            "median_price_mad": round(float(data["price_mad"].median())),
            "mean_price_mad": round(float(data["price_mad"].mean())),
            "median_price_per_m2": round(float(price_per_m2.median())),
            "mean_surface_m2": round(float(data["surface_m2"].mean()), 1),
            "min_price_mad": round(float(data["price_mad"].min())),
            "max_price_mad": round(float(data["price_mad"].max())),
            "sources": {
                str(source): int(count)
                for source, count in data["source"].value_counts().items()
            },
        }

    @staticmethod
    def _completeness(item: ListingInput) -> float:
        values = [
            item.name,
            item.advertised_price_mad,
            item.property.surface_m2,
            item.property.rooms,
            item.property.bedrooms,
            item.property.bathrooms,
            item.property.city,
            item.property.neighborhood,
            item.url,
        ]
        return sum(value not in (None, "", "Unknown") for value in values) / len(values)

    def compare_properties(
        self,
        listings: list[ListingInput],
        budget_mad: float | None = None,
        preferred_city: str | None = None,
        preferred_neighborhood: str | None = None,
        preferred_surface_m2: float | None = None,
    ) -> list[dict[str, Any]]:
        if not 2 <= len(listings) <= 20:
            raise ValueError("Provide between 2 and 20 properties.")
        if budget_mad is not None and budget_mad <= 0:
            raise ValueError("budget_mad must be positive.")

        results = []
        for listing in listings:
            if listing.advertised_price_mad <= 0:
                raise ValueError("Every advertised price must be positive.")
            estimate = self.predict_price(listing.property)
            estimated_price = float(estimate["estimated_price_mad"])
            deviation = (listing.advertised_price_mad - estimated_price) / estimated_price

            value_score = float(np.clip(60 - deviation * 100, 0, 100))
            budget_score = 100.0
            if budget_mad:
                over_budget = max(0.0, listing.advertised_price_mad - budget_mad)
                budget_score = float(np.clip(100 - (over_budget / budget_mad) * 200, 0, 100))

            location_score = 50.0
            if preferred_city:
                location_score = (
                    80.0
                    if listing.property.city.casefold() == preferred_city.strip().casefold()
                    else 0.0
                )
            if preferred_neighborhood and (
                listing.property.neighborhood.casefold()
                == preferred_neighborhood.strip().casefold()
            ):
                location_score = 100.0

            surface_score = 70.0
            if preferred_surface_m2:
                difference = abs(listing.property.surface_m2 - preferred_surface_m2)
                surface_score = float(
                    np.clip(100 - (difference / preferred_surface_m2) * 100, 0, 100)
                )

            completeness = self._completeness(listing) * 100
            score = (
                value_score * 0.35
                + budget_score * 0.25
                + location_score * 0.2
                + surface_score * 0.1
                + completeness * 0.1
            )
            results.append(
                {
                    "name": listing.name,
                    "url": listing.url,
                    "advertised_price_mad": round(listing.advertised_price_mad),
                    "estimated_price_mad": round(estimated_price),
                    "price_per_m2": round(
                        listing.advertised_price_mad / listing.property.surface_m2
                    ),
                    "difference_percent": round(deviation * 100, 1),
                    "completeness_percent": round(completeness),
                    "score": round(score, 1),
                    "city": listing.property.city,
                    "neighborhood": listing.property.neighborhood,
                    "surface_m2": listing.property.surface_m2,
                    "explanation": (
                        f"Valeur {value_score:.0f}/100, budget {budget_score:.0f}/100, "
                        f"localisation {location_score:.0f}/100."
                    ),
                }
            )

        ranked = sorted(results, key=lambda item: item["score"], reverse=True)
        for rank, item in enumerate(ranked, start=1):
            item["rank"] = rank
        return ranked

    def recommend_properties(
        self,
        budget_mad: float,
        city: str,
        neighborhood: str | None = None,
        min_surface_m2: float = 0,
        min_bedrooms: float = 0,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        if budget_mad <= 0:
            raise ValueError("budget_mad must be positive.")
        if not 1 <= limit <= 20:
            raise ValueError("limit must be between 1 and 20.")

        data = self.data.copy()
        data = data[
            (data["price_mad"] <= budget_mad)
            & (data["surface_m2"] >= min_surface_m2)
            & (data["bedrooms"].fillna(0) >= min_bedrooms)
            & (data["city"].str.casefold() == city.strip().casefold())
        ].copy()
        if neighborhood:
            local = data[
                data["neighborhood"].fillna("").str.casefold()
                == neighborhood.strip().casefold()
            ]
            if not local.empty:
                data = local
        if data.empty:
            return []

        data["price_per_m2"] = data["price_mad"] / data["surface_m2"]
        data["budget_fit"] = 1 - (budget_mad - data["price_mad"]).abs() / budget_mad
        data["value_score"] = 1 - (
            data["price_per_m2"] / max(data["price_per_m2"].max(), 1)
        )
        data["recommendation_score"] = data["budget_fit"] * 0.55 + data["value_score"] * 0.45
        selected = data.sort_values("recommendation_score", ascending=False).head(limit)
        fields = [
            "source", "title", "price_mad", "surface_m2", "rooms", "bedrooms",
            "bathrooms", "city", "neighborhood", "url", "price_per_m2",
            "recommendation_score",
        ]
        records = selected[fields].replace({np.nan: None}).to_dict(orient="records")
        for rank, record in enumerate(records, start=1):
            record["rank"] = rank
            record["price_per_m2"] = round(record["price_per_m2"])
            record["recommendation_score"] = round(record["recommendation_score"] * 100, 1)
        return records
