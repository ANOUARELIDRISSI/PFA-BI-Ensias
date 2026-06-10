from __future__ import annotations

import json

import pandas as pd

from ml.runner import read_model_performance


def test_read_model_performance(tmp_path) -> None:
    report = {
        "trained_at": "2026-06-10T00:00:00+00:00",
        "dataset_rows": 20,
        "best_model": "extra_trees",
        "models": {"extra_trees": {"test_mae": 100}},
        "error_by_price_band": [],
    }
    path = tmp_path / "report.json"
    path.write_text(json.dumps(report), encoding="utf-8")

    result = read_model_performance(path)

    assert result["best_model"] == "extra_trees"
    assert result["best_metrics"]["test_mae"] == 100
