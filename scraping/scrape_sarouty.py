from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

try:
    from scraping.schema import FIELDS, Listing
except ModuleNotFoundError:
    from schema import FIELDS, Listing

API_URL = "https://b2c-be-prod.api.sarouty.ma/api/properties"
OUTPUT_DIR = Path("data/raw")
USER_AGENT = (
    "Mozilla/5.0 (compatible; PFA-BI-Ensias/0.1; "
    "+https://github.com/ANOUARELIDRISSI/PFA-BI-Ensias)"
)
def fetch_page(page: int, limit: int, transaction: str = "sale") -> dict[str, Any]:
    response = requests.get(
        API_URL,
        params={
            "property_category_id": 2 if transaction == "rent" else 1,
            "property_property_housing_id": 1,
            "page": page,
            "limit": limit,
        },
        headers={"User-Agent": USER_AGENT, "Accept-Language": "fr,en;q=0.8"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def normalize(
    item: dict[str, Any],
    page: int,
    scraped_at: str,
    transaction: str = "sale",
) -> dict[str, Any]:
    price_data = item.get("price") or {}
    price_value = price_data.get("price")
    location = item.get("location_name")
    city = item.get("location_url_slug")
    if city and city.lower() not in str(location).lower():
        location = f"{location}, {city.title()}"

    row = Listing(
        source="sarouty",
        source_id=item.get("property_id"),
        scraped_at=scraped_at,
        published_at=item.get("property_date_creation"),
        page=page,
        transaction_type=transaction,
        property_type=item.get("property_housing_type"),
        title=item.get("property_title_fr") or item.get("property_title_en"),
        description=item.get("property_description_fr") or item.get("property_description_en"),
        price=f"{price_value} MAD" if price_value is not None else None,
        price_mad=price_value,
        location=location,
        city=city.title() if city else None,
        neighborhood=item.get("location_name"),
        latitude=item.get("latitude"),
        longitude=item.get("longitude"),
        surface_m2=item.get("property_sqft"),
        rooms=item.get("property_bedroom_id"),
        bedrooms=item.get("total_bedroom"),
        bathrooms=item.get("total_bathroom"),
        floor=item.get("property_floor"),
        total_floors=item.get("property_total_floor"),
        property_condition=item.get("property_condition"),
        construction_year=item.get("construction_year"),
        furnished=item.get("property_furnished"),
        elevator=item.get("property_elevator"),
        parking=item.get("property_parking"),
        terrace=item.get("property_terrace"),
        balcony=item.get("property_balcony"),
        security=item.get("property_security"),
        url=f"https://www.sarouty.ma/property/{item.get('property_id')}/",
    )
    return row.to_dict()


def scrape(
    min_listings: int,
    delay: float,
    page_size: int = 100,
    transaction: str = "sale",
) -> list[dict[str, Any]]:
    scraped_at = datetime.now(timezone.utc).isoformat()
    listings: dict[int, dict[str, Any]] = {}
    page = 1

    while len(listings) < min_listings:
        print(f"Scraping Sarouty API page {page}")
        payload = fetch_page(page=page, limit=page_size, transaction=transaction)
        items = payload.get("data", {}).get("data", [])
        if not items:
            break

        for item in items:
            row = normalize(
                item, page=page, scraped_at=scraped_at, transaction=transaction
            )
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


def save_outputs(
    rows: list[dict[str, Any]],
    overwrite: bool = False,
    transaction: str = "sale",
) -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if overwrite:
        csv_path = OUTPUT_DIR / f"sarouty_apartments_{transaction}.csv"
        json_path = OUTPUT_DIR / f"sarouty_apartments_{transaction}.json"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = OUTPUT_DIR / f"sarouty_apartments_{transaction}_{timestamp}.csv"
        json_path = OUTPUT_DIR / f"sarouty_apartments_{transaction}_{timestamp}.json"

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
    parser.add_argument("--transaction", choices=["sale", "rent"], default="sale")
    parser.add_argument("--overwrite", action="store_true", help="Write stable filenames instead of timestamped files.")
    args = parser.parse_args()

    rows = scrape(
        min_listings=args.min_listings,
        delay=args.delay,
        transaction=args.transaction,
    )
    csv_path, json_path = save_outputs(
        rows, overwrite=args.overwrite, transaction=args.transaction
    )
    print(f"Saved {len(rows)} listings to {csv_path} and {json_path}")


if __name__ == "__main__":
    main()
