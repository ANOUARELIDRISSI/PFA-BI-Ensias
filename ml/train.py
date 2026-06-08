from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ml.clean_data import DEFAULT_OUTPUT, save_clean_data


MODEL_PATH = Path("models/best_price_model.joblib")
REPORT_PATH = Path("reports/model_metrics.json")
NUMERIC_FEATURES = ["surface_m2", "rooms", "bedrooms", "bathrooms"]
CATEGORICAL_FEATURES = ["source", "city", "neighborhood", "property_type", "furnished"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "price_mad"


def build_preprocessor() -> ColumnTransformer:
    numeric = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", min_frequency=2)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric, NUMERIC_FEATURES),
            ("categorical", categorical, CATEGORICAL_FEATURES),
        ]
    )


def candidate_models() -> dict[str, object]:
    return {
        "ridge": Ridge(alpha=10.0),
        "random_forest": RandomForestRegressor(
            n_estimators=500,
            min_samples_leaf=2,
            max_features=0.8,
            random_state=42,
            n_jobs=-1,
        ),
        "extra_trees": ExtraTreesRegressor(
            n_estimators=500,
            min_samples_leaf=2,
            max_features=0.9,
            random_state=42,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingRegressor(
            n_estimators=300,
            learning_rate=0.03,
            max_depth=2,
            loss="huber",
            random_state=42,
        ),
    }


def make_pipeline(model: object) -> TransformedTargetRegressor:
    regressor = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("model", model),
        ]
    )
    return TransformedTargetRegressor(
        regressor=regressor,
        func=np.log1p,
        inverse_func=np.expm1,
    )


def evaluate(
    data: pd.DataFrame,
    test_size: float = 0.2,
) -> tuple[str, object, dict[str, dict[str, float]], pd.DataFrame, pd.Series]:
    x = data[FEATURES]
    y = data[TARGET]
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=test_size,
        random_state=42,
    )
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    results: dict[str, dict[str, float]] = {}
    fitted_models: dict[str, object] = {}

    for name, model in candidate_models().items():
        pipeline = make_pipeline(model)
        cv_mae = -cross_val_score(
            pipeline,
            x_train,
            y_train,
            scoring="neg_mean_absolute_error",
            cv=cv,
            n_jobs=-1,
        )
        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)

        results[name] = {
            "cv_mae_mean": round(float(cv_mae.mean()), 2),
            "cv_mae_std": round(float(cv_mae.std()), 2),
            "test_mae": round(float(mean_absolute_error(y_test, predictions)), 2),
            "test_rmse": round(float(mean_squared_error(y_test, predictions) ** 0.5), 2),
            "test_r2": round(float(r2_score(y_test, predictions)), 4),
        }
        fitted_models[name] = pipeline

    best_name = min(results, key=lambda name: results[name]["cv_mae_mean"])
    return best_name, fitted_models[best_name], results, x_test, y_test


def train(data_path: Path, model_path: Path, report_path: Path) -> dict[str, object]:
    if not data_path.exists():
        save_clean_data(data_path)

    data = pd.read_csv(data_path)
    best_name, best_model, results, x_test, y_test = evaluate(data)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, model_path)

    test_predictions = best_model.predict(x_test)
    sample_errors = pd.DataFrame(
        {
            "actual_price_mad": y_test,
            "predicted_price_mad": np.round(test_predictions, 0),
            "absolute_error_mad": np.round(np.abs(y_test - test_predictions), 0),
        }
    ).sort_values("absolute_error_mad", ascending=False)

    report: dict[str, object] = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset_rows": int(len(data)),
        "features": FEATURES,
        "target": TARGET,
        "selection_metric": "lowest 5-fold cross-validation MAE",
        "best_model": best_name,
        "models": results,
        "largest_test_errors": sample_errors.head(10).to_dict(orient="records"),
        "model_path": str(model_path),
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and select a Moroccan property price model.")
    parser.add_argument("--data", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", type=Path, default=MODEL_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    report = train(args.data, args.model, args.report)
    best = report["best_model"]
    metrics = report["models"][best]
    print(f"Best model: {best}")
    print(f"CV MAE: {metrics['cv_mae_mean']:.2f} MAD")
    print(f"Test MAE: {metrics['test_mae']:.2f} MAD")
    print(f"Test RMSE: {metrics['test_rmse']:.2f} MAD")
    print(f"Test R2: {metrics['test_r2']:.4f}")


if __name__ == "__main__":
    main()
