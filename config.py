"""Shared project configuration loaded from the repository root."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
ROOT_ENV_PATH = PROJECT_ROOT / ".env"


def load_project_env(*, override: bool = False) -> Path:
    """Load the single supported .env file from the repository root."""
    load_dotenv(dotenv_path=ROOT_ENV_PATH, override=override)
    return ROOT_ENV_PATH


def require_env(name: str) -> str:
    """Return a required environment variable after loading the root .env."""
    load_project_env()
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"{name} est absente. Ajoutez-la dans {ROOT_ENV_PATH}."
        )
    return value
