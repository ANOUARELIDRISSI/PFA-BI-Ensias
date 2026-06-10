from __future__ import annotations

import subprocess

import pytest

from scraping import runner


def test_runner_builds_approved_mubawab_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(command, 0, "Saved 150 listings", "")

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    result = runner.run_scraper("mubawab", "rent", min_listings=150, max_pages=12)

    command = captured["command"]
    assert isinstance(command, list)
    assert "--transaction" in command and "rent" in command
    assert "--max-pages" in command and "12" in command
    assert result["success"] is True
    assert result["csv_path"].endswith("mubawab_apartments_rent.csv")


def test_runner_rejects_unapproved_source() -> None:
    with pytest.raises(ValueError, match="Source non autorisee"):
        runner.run_scraper("unknown", "sale")
