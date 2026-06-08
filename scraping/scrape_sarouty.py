from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


API_URL = "https://b2c-be-prod.api.sarouty.ma/api/properties"
OUTPUT_DIR = Path("data/raw")
USER_AGENT = (
    "Mozilla/5.0 (compatible; PFA-BI-Ensias/0.1; "
    "+https://github.com/ANOUARELIDRISSI/PFA-BI-Ensias)"
)
FIELDS = [
    "source",
    "source_id",
    "scraped_at",
    "page",
    "title",
    "price",
    "price_mad",
    "location",
    "property_type",
    "surface_m2",
    "rooms",
    "bedrooms",
    "bathrooms",
    "furnished",
    "published_at",
    "url",
]


def fetch_page(page: int, limit: int) -> dict[str, Any]:
    response = requests.get(
        API_URL,
        params={
            "property_category_id": 1,
            "property_property_housing_id": 1,
            "page": page,
            "limit": limit,
        },
        headers={"User-Agent": USER_AGENT, "Accept-Language": "fr,en;q=0.8"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def normalize(item: dict[str, Any], page: int, scraped_at: str) -> dict[str, Any]:
    price_data = item.get("price") or {}
    price_value = price_data.get("price")
    location = item.get("location_name")
    city = item.get("location_url_slug")
    if city and city.lower() not in str(location).lower():
        location = f"{location}, {city.title()}"

    return {
        "source": "sarouty",
        "source_id": item.get("property_id"),
        "scraped_at": scraped_at,
        "page": page,
        "title": item.get("property_title_fr") or item.get("property_title_en"),
        "price": f"{price_value} MAD" if price_value is not None else None,
        "price_mad": price_value,
        "location": location,
        "property_type": item.get("property_housing_type"),
        "surface_m2": item.get("property_sqft"),
        "rooms": item.get("property_bedroom_id"),
        "bedrooms": item.get("total_bedroom"),
        "bathrooms": item.get("total_bathroom"),
        "furnished": item.get("property_furnished"),
        "published_at": item.get("property_date_creation"),
        "url": f"https://www.sarouty.ma/property/{item.get('property_id')}/",
    }


def scrape(min_listings: int, delay: float, page_size: int = 100) -> list[dict[str, Any]]:
    scraped_at = datetime.now(timezone.utc).isoformat()
    listings: dict[int, dict[str, Any]] = {}
    page = 1

    while len(listings) < min_listings:
        print(f"Scraping Sarouty API page {page}")
        payload = fetch_page(page=page, limit=page_size)
        items = payload.get("data", {}).get("data", [])
        if not items:
            break

        for item in items:
            row = normalize(item, page=page, scraped_at=scraped_at)
            if row["source_id"] is not None:
                listings[int(row["source_id"])] = row

        print(f"  Collected {len(listings)} unique listings")
        page += 1
        if len(listings) < min_listings:
            time.sleep(delay)

    rows = list(listings.values())
    if len(rows) < min_listings:
        raise RuntimeError(
            f"Only {len(rows)} unique listings were collected; "
            f"the requested minimum is {min_listings}."
        )
    return rows


def save_outputs(rows: list[dict[str, Any]], overwrite: bool = False) -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if overwrite:
        csv_path = OUTPUT_DIR / "sarouty_apartments_sale.csv"
        json_path = OUTPUT_DIR / "sarouty_apartments_sale.json"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = OUTPUT_DIR / f"sarouty_apartments_sale_{timestamp}.csv"
        json_path = OUTPUT_DIR / f"sarouty_apartments_sale_{timestamp}.json"

    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)

    return csv_path, json_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect apartment sale listings from Sarouty Morocco.")
    parser.add_argument("--min-listings", type=int, default=150, help="Minimum unique listings to collect.")
    parser.add_argument("--delay", type=float, default=10.0, help="Delay between requests in seconds.")
    parser.add_argument("--overwrite", action="store_true", help="Write stable filenames instead of timestamped files.")
    args = parser.parse_args()

    rows = scrape(min_listings=args.min_listings, delay=args.delay)
    csv_path, json_path = save_outputs(rows, overwrite=args.overwrite)
    print(f"Saved {len(rows)} listings to {csv_path} and {json_path}")


if __name__ == "__main__":
    main()
