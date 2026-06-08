from __future__ import annotations

import argparse
import csv
import json
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://www.mubawab.ma"
START_URL = f"{BASE_URL}/en/sc/apartments-for-sale"
OUTPUT_DIR = Path("data/raw")
USER_AGENT = (
    "Mozilla/5.0 (compatible; PFA-BI-Ensias/0.1; "
    "+https://github.com/ANOUARELIDRISSI/PFA-BI-Ensias)"
)


@dataclass
class Listing:
    source: str
    scraped_at: str
    page: int
    title: str | None
    price: str | None
    price_mad: int | None
    location: str | None
    surface_m2: int | None
    rooms: int | None
    bedrooms: int | None
    bathrooms: int | None
    description: str | None
    url: str | None


def clean_text(value: str | None) -> str | None:
    if not value:
        return None
    text = re.sub(r"\s+", " ", value).strip()
    return text or None


def parse_int(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"\d[\d\s.,]*", value)
    if not match:
        return None
    digits = re.sub(r"\D", "", match.group(0))
    return int(digits) if digits else None


def page_url(page: int) -> str:
    if page <= 1:
        return START_URL
    return f"{START_URL}:p:{page}"


def fetch_page(url: str) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "en,fr;q=0.9"},
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def find_listing_cards(soup: BeautifulSoup) -> list[Tag]:
    selectors = [
        "li.listingBox",
        "div.listingBox",
        "li[class*='listingBox']",
        "div[class*='listingBox']",
    ]
    cards: list[Tag] = []
    for selector in selectors:
        cards = [card for card in soup.select(selector) if isinstance(card, Tag)]
        if cards:
            break
    return cards


def first_text(card: Tag, selectors: Iterable[str]) -> str | None:
    for selector in selectors:
        element = card.select_one(selector)
        if element:
            text = clean_text(element.get_text(" ", strip=True))
            if text:
                return text
    return None


def first_link(card: Tag) -> str | None:
    for selector in ("a[href*='/en/a/']", "a[href*='/fr/a/']", "a[href]"):
        link = card.select_one(selector)
        if link and link.get("href"):
            return urljoin(BASE_URL, str(link["href"]))
    return None


def parse_features(card: Tag, full_text: str) -> tuple[int | None, int | None, int | None, int | None]:
    surface = parse_int(
        first_text(card, ("span.tagProp:-soup-contains('m')", "span[class*='surface']", "i.icon-triangle + span"))
    )

    if surface is None:
        surface_match = re.search(r"(\d[\d\s]*)\s*m[²2]", full_text, flags=re.IGNORECASE)
        surface = parse_int(surface_match.group(1)) if surface_match else None

    rooms_match = re.search(r"(\d+)\s+room", full_text, flags=re.IGNORECASE)
    bedrooms_match = re.search(r"(\d+)\s+bedroom", full_text, flags=re.IGNORECASE)
    bathrooms_match = re.search(r"(\d+)\s+bathroom", full_text, flags=re.IGNORECASE)

    rooms = parse_int(rooms_match.group(1)) if rooms_match else None
    bedrooms = parse_int(bedrooms_match.group(1)) if bedrooms_match else None
    bathrooms = parse_int(bathrooms_match.group(1)) if bathrooms_match else None
    return surface, rooms, bedrooms, bathrooms


def parse_listing(card: Tag, page: int, scraped_at: str) -> Listing | None:
    full_text = clean_text(card.get_text(" ", strip=True)) or ""
    title = first_text(card, ("h2.listingTit", "h2", "a[title]"))
    price = first_text(card, ("span.priceTag", "span[class*='price']", ".priceTag"))
    location = first_text(card, (".listingH3", "h3", "span[class*='location']", ".location"))
    description = first_text(card, (".listingP", "p[class*='description']", "p"))
    url = first_link(card)
    surface, rooms, bedrooms, bathrooms = parse_features(card, full_text)

    if not any([title, price, location, url]):
        return None

    return Listing(
        source="mubawab",
        scraped_at=scraped_at,
        page=page,
        title=title,
        price=price,
        price_mad=parse_int(price),
        location=location,
        surface_m2=surface,
        rooms=rooms,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        description=description,
        url=url,
    )


def scrape(max_pages: int, delay: float, min_listings: int = 0) -> list[Listing]:
    scraped_at = datetime.now(timezone.utc).isoformat()
    listings: list[Listing] = []

    for page in range(1, max_pages + 1):
        url = page_url(page)
        print(f"Scraping page {page}: {url}")
        soup = BeautifulSoup(fetch_page(url), "html.parser")
        cards = find_listing_cards(soup)
        page_listings = [listing for card in cards if (listing := parse_listing(card, page, scraped_at))]
        listings.extend(page_listings)
        print(f"  Found {len(page_listings)} listings")

        unique_count = len({listing.url for listing in listings if listing.url})
        if min_listings and unique_count >= min_listings:
            break

        if page < max_pages:
            time.sleep(delay)

    unique_listings = {listing.url: listing for listing in listings if listing.url}
    return list(unique_listings.values())


def save_outputs(listings: list[Listing], output_dir: Path = OUTPUT_DIR, overwrite: bool = False) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    if overwrite:
        csv_path = output_dir / "mubawab_apartments_sale.csv"
        json_path = output_dir / "mubawab_apartments_sale.json"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = output_dir / f"mubawab_apartments_sale_{timestamp}.csv"
        json_path = output_dir / f"mubawab_apartments_sale_{timestamp}.json"
    rows = [asdict(listing) for listing in listings]

    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(Listing.__dataclass_fields__.keys()))
        writer.writeheader()
        writer.writerows(rows)

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)

    return csv_path, json_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape apartment sale listings from Mubawab Morocco.")
    parser.add_argument("--max-pages", type=int, default=10, help="Maximum number of listing pages to scrape.")
    parser.add_argument("--min-listings", type=int, default=150, help="Minimum number of unique listings to collect.")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between page requests in seconds.")
    parser.add_argument("--overwrite", action="store_true", help="Write stable filenames instead of timestamped files.")
    args = parser.parse_args()

    listings = scrape(max_pages=args.max_pages, delay=args.delay, min_listings=args.min_listings)
    if len(listings) < args.min_listings:
        raise RuntimeError(
            f"Only {len(listings)} unique listings were collected; "
            f"the requested minimum is {args.min_listings}."
        )
    csv_path, json_path = save_outputs(listings, overwrite=args.overwrite)
    print(f"Saved {len(listings)} listings to {csv_path} and {json_path}")


if __name__ == "__main__":
    main()
