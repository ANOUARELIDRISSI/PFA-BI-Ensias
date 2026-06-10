from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS


ALLOWED_DOMAINS = {
    "mubawab.ma": "Mubawab",
    "sarouty.ma": "Sarouty",
    "avito.ma": "Avito",
    "agenz.ma": "Agenz",
}
USER_AGENT = (
    "Mozilla/5.0 (compatible; PFA-BI-Ensias/0.1; "
    "+https://github.com/ANOUARELIDRISSI/PFA-BI-Ensias)"
)


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    source: str
    snippet: str
    price_mad: int | None
    location: str | None
    checked_at: str
    verified: bool
    status_code: int | None


def allowed_source(url: str) -> str | None:
    hostname = (urlparse(url).hostname or "").lower()
    hostname = hostname.removeprefix("www.")
    for domain, name in ALLOWED_DOMAINS.items():
        if hostname == domain or hostname.endswith(f".{domain}"):
            return name
    return None


def parse_price(text: str) -> int | None:
    patterns = [
        r"(\d[\d\s.,]{2,})\s*(?:MAD|DH|DHS)\b",
        r"(?:prix|price)\s*[:\-]?\s*(\d[\d\s.,]{2,})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            digits = re.sub(r"\D", "", match.group(1))
            if digits:
                return int(digits)
    return None


def verify_result(url: str, timeout: int = 10) -> tuple[bool, int | None, str]:
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "fr,en;q=0.8"},
            timeout=timeout,
            allow_redirects=True,
        )
        source = allowed_source(response.url)
        verified = response.status_code == 200 and source is not None
        text = ""
        if verified:
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(" ", strip=True)[:5_000]
        return verified, response.status_code, text
    except requests.RequestException:
        return False, None, ""


def _queries(
    city: str,
    transaction: str,
    property_type: str,
    neighborhood: str | None,
) -> Iterable[str]:
    location = f"{neighborhood} {city}" if neighborhood else city
    transaction_term = "location louer" if transaction == "rent" else "vente acheter"
    for domain in ALLOWED_DOMAINS:
        yield f"site:{domain} {property_type} {transaction_term} {location} Maroc"


def search_properties(
    city: str,
    transaction: str = "sale",
    property_type: str = "appartement",
    neighborhood: str | None = None,
    max_results: int = 10,
    verify: bool = True,
) -> list[dict[str, object]]:
    if transaction not in {"sale", "rent"}:
        raise ValueError("transaction must be 'sale' or 'rent'.")
    if not city.strip():
        raise ValueError("city is required.")
    if not 1 <= max_results <= 30:
        raise ValueError("max_results must be between 1 and 30.")

    candidates: dict[str, dict[str, str]] = {}
    per_query = max(3, (max_results // len(ALLOWED_DOMAINS)) + 2)
    with DDGS(timeout=10) as client:
        for query in _queries(city, transaction, property_type, neighborhood):
            for item in client.text(
                query,
                region="ma-fr",
                safesearch="moderate",
                max_results=per_query,
            ):
                url = str(item.get("href") or item.get("url") or "").strip()
                source = allowed_source(url)
                if not url or not source:
                    continue
                canonical = url.split("#", 1)[0].rstrip("/")
                candidates.setdefault(
                    canonical,
                    {
                        "title": str(item.get("title") or "Annonce immobiliere"),
                        "url": canonical,
                        "source": source,
                        "snippet": str(item.get("body") or item.get("description") or ""),
                    },
                )
                if len(candidates) >= max_results * 2:
                    break

    checked_at = datetime.now(timezone.utc).isoformat()
    results: list[SearchResult] = []
    for item in list(candidates.values())[:max_results]:
        page_text = ""
        verified = False
        status_code = None
        if verify:
            verified, status_code, page_text = verify_result(item["url"])
        combined = " ".join([item["title"], item["snippet"], page_text])
        results.append(
            SearchResult(
                title=item["title"],
                url=item["url"],
                source=item["source"],
                snippet=item["snippet"],
                price_mad=parse_price(combined),
                location=neighborhood or city,
                checked_at=checked_at,
                verified=verified,
                status_code=status_code,
            )
        )

    results.sort(key=lambda item: (not item.verified, item.source, item.title))
    return [asdict(item) for item in results]
