"""Controlled orchestration for cleaning, training, and model reporting."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from ml.clean_data import DEFAULT_OUTPUT, save_clean_data
from ml.train import MODEL_PATH, REPORT_PATH, train


def clean_dataset(output_path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    output = save_clean_data(output_path)
    data = pd.read_csv(output)
    return {
        "success": True,
        "rows": int(len(data)),
        "columns": int(len(data.columns)),
        "output_path": str(output.resolve()),
        "sources": {
            str(source): int(count)
            for source, count in data["source"].value_counts().items()
        },
    }


def train_price_model(
    data_path: Path = DEFAULT_OUTPUT,
    model_path: Path = MODEL_PATH,
    report_path: Path = REPORT_PATH,
) -> dict[str, Any]:
    report = train(data_path, model_path, report_path)
    best_name = str(report["best_model"])
    return {
        "success": True,
        "best_model": best_name,
        "dataset_rows": report["dataset_rows"],
        "metrics": report["models"][best_name],
        "model_path": str(model_path.resolve()),
        "report_path": str(report_path.resolve()),
    }


def read_model_performance(report_path: Path = REPORT_PATH) -> dict[str, Any]:
    if not report_path.exists():
        raise FileNotFoundError(
            "Rapport ML absent. Lancez d'abord le nettoyage et l'entrainement."
        )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    best_name = str(report["best_model"])
    return {
        "trained_at": report["trained_at"],
        "dataset_rows": report["dataset_rows"],
        "best_model": best_name,
        "best_metrics": report["models"][best_name],
        "models": report["models"],
        "error_by_price_band": report.get("error_by_price_band", []),
    }
