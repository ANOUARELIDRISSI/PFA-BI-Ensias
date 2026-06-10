"""Controlled execution of the project's approved scraping scripts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRAPERS = {
    "mubawab": PROJECT_ROOT / "scraping" / "scrape_mubawab.py",
    "sarouty": PROJECT_ROOT / "scraping" / "scrape_sarouty.py",
}


def run_scraper(
    source: str,
    transaction: str,
    min_listings: int = 150,
    max_pages: int = 20,
    timeout_seconds: int = 600,
) -> dict[str, Any]:
    """Run one approved scraper and return structured execution details."""
    normalized_source = source.strip().lower()
    normalized_transaction = transaction.strip().lower()
    if normalized_source not in SCRAPERS:
        raise ValueError(f"Source non autorisee: {source}")
    if normalized_transaction not in {"sale", "rent"}:
        raise ValueError("transaction doit etre 'sale' ou 'rent'.")
    if not 1 <= min_listings <= 1_000:
        raise ValueError("min_listings doit etre compris entre 1 et 1000.")
    if not 1 <= max_pages <= 100:
        raise ValueError("max_pages doit etre compris entre 1 et 100.")

    command = [
        sys.executable,
        str(SCRAPERS[normalized_source]),
        "--transaction",
        normalized_transaction,
        "--min-listings",
        str(min_listings),
        "--overwrite",
    ]
    if normalized_source == "mubawab":
        command.extend(["--max-pages", str(max_pages)])

    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_seconds,
        check=False,
    )
    output_base = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / f"{normalized_source}_apartments_{normalized_transaction}"
    )
    return {
        "success": completed.returncode == 0,
        "source": normalized_source,
        "transaction": normalized_transaction,
        "return_code": completed.returncode,
        "csv_path": str(output_base.with_suffix(".csv")),
        "json_path": str(output_base.with_suffix(".json")),
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }
