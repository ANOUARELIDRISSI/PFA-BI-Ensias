from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd

from ml.train import MODEL_PATH


def predict_price(
    model_path: Path,
    surface_m2: float,
    rooms: float,
    bedrooms: float,
    bathrooms: float,
    city: str,
    neighborhood: str,
    furnished: str,
    source: str = "unknown",
) -> float:
    model = joblib.load(model_path)
    listing = pd.DataFrame(
        [
            {
                "surface_m2": surface_m2,
                "rooms": rooms,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "source": source,
                "city": city,
                "neighborhood": neighborhood,
                "property_type": "Appartement",
                "furnished": furnished,
            }
        ]
    )
    return float(model.predict(listing)[0])


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict an apartment sale price in Morocco.")
    parser.add_argument("--model", type=Path, default=MODEL_PATH)
    parser.add_argument("--surface", type=float, required=True)
    parser.add_argument("--rooms", type=float, required=True)
    parser.add_argument("--bedrooms", type=float, required=True)
    parser.add_argument("--bathrooms", type=float, required=True)
    parser.add_argument("--city", required=True)
    parser.add_argument("--neighborhood", default="Unknown")
    parser.add_argument("--furnished", default="UNKNOWN")
    parser.add_argument("--source", default="unknown")
    args = parser.parse_args()

    prediction = predict_price(
        model_path=args.model,
        surface_m2=args.surface,
        rooms=args.rooms,
        bedrooms=args.bedrooms,
        bathrooms=args.bathrooms,
        city=args.city,
        neighborhood=args.neighborhood,
        furnished=args.furnished,
        source=args.source,
    )
    print(f"Prix estime : {prediction:,.0f} MAD")


if __name__ == "__main__":
    main()
