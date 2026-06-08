from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
DEFAULT_OUTPUT = PROCESSED_DIR / "real_estate_clean.csv"


def _read_csv_files(raw_dir: Path) -> pd.DataFrame:
    files = sorted(raw_dir.glob("*_apartments_sale_*.csv")) + sorted(raw_dir.glob("*_apartments_sale.csv"))
    if not files:
        raise FileNotFoundError(f"No raw CSV files found in {raw_dir}")

    frames = []
    for file in files:
        frame = pd.read_csv(file)
        frame["raw_file"] = file.name
        frames.append(frame)
    return pd.concat(frames, ignore_index=True, sort=False)


def _to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _split_location(value: object) -> tuple[str | None, str | None]:
    if pd.isna(value):
        return None, None
    parts = [part.strip() for part in str(value).split(",") if part.strip()]
    if not parts:
        return None, None
    if len(parts) == 1:
        return None, parts[0].title()
    neighborhood = parts[0].title()
    city = parts[-1].title()
    return neighborhood, city


def _clip_iqr(frame: pd.DataFrame, column: str, multiplier: float = 1.5) -> pd.DataFrame:
    q1 = frame[column].quantile(0.25)
    q3 = frame[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    return frame[(frame[column] >= lower) & (frame[column] <= upper)].copy()


def clean(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    data = _read_csv_files(raw_dir)

    keep_columns = [
        "source",
        "title",
        "price_mad",
        "location",
        "property_type",
        "surface_m2",
        "rooms",
        "bedrooms",
        "bathrooms",
        "furnished",
        "url",
    ]
    for column in keep_columns:
        if column not in data.columns:
            data[column] = np.nan

    data = data[keep_columns].copy()
    data["price_mad"] = _to_numeric(data["price_mad"])
    data["surface_m2"] = _to_numeric(data["surface_m2"])
    data["rooms"] = _to_numeric(data["rooms"])
    data["bedrooms"] = _to_numeric(data["bedrooms"])
    data["bathrooms"] = _to_numeric(data["bathrooms"])

    locations = data["location"].apply(_split_location)
    data["neighborhood"] = locations.apply(lambda item: item[0])
    data["city"] = locations.apply(lambda item: item[1])
    data["property_type"] = data["property_type"].fillna("Appartement")
    data["furnished"] = data["furnished"].fillna("UNKNOWN")

    data = data.drop_duplicates(subset=["source", "url"], keep="last")
    data = data.dropna(subset=["price_mad", "surface_m2", "city"])
    data = data[
        (data["price_mad"] >= 100_000)
        & (data["price_mad"] <= 20_000_000)
        & (data["surface_m2"] >= 20)
        & (data["surface_m2"] <= 500)
    ].copy()

    data["price_per_m2"] = data["price_mad"] / data["surface_m2"]
    data = data[(data["price_per_m2"] >= 2_000) & (data["price_per_m2"] <= 80_000)].copy()
    data = _clip_iqr(data, "price_mad", multiplier=2.0)
    data = _clip_iqr(data, "surface_m2", multiplier=2.0)

    data["rooms"] = data["rooms"].fillna(data["bedrooms"])
    data["bedrooms"] = data["bedrooms"].fillna(data["rooms"])
    data["bathrooms"] = data["bathrooms"].fillna(data["bathrooms"].median())
    data["rooms"] = data["rooms"].fillna(data["rooms"].median())
    data["bedrooms"] = data["bedrooms"].fillna(data["bedrooms"].median())

    data["source"] = data["source"].str.lower().fillna("unknown")
    data["city"] = data["city"].str.strip().str.title()
    data["neighborhood"] = data["neighborhood"].fillna("Unknown").str.strip().str.title()

    return data.reset_index(drop=True)


def save_clean_data(output_path: Path = DEFAULT_OUTPUT) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = clean()
    data.to_csv(output_path, index=False)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean raw Moroccan real-estate listings.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = save_clean_data(args.output)
    rows = pd.read_csv(output).shape[0]
    print(f"Saved {rows} cleaned rows to {output}")


if __name__ == "__main__":
    main()
