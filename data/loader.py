"""Data loader helpers for reading procurement mock data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MOCK_DATA_DIR = Path(__file__).resolve().parent.parent / "mock_data"


def _load_json(filename: str) -> list[dict[str, Any]]:
    """Load and parse one JSON file from mock_data/."""
    file_path = MOCK_DATA_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Mock data file not found: {file_path}")
    return json.loads(file_path.read_text(encoding="utf-8"))


def load_requests() -> list[dict[str, Any]]:
    """Return all purchase request records."""
    return _load_json("requests.json")


def load_policies() -> list[dict[str, Any]]:
    """Return all procurement policy records."""
    return _load_json("policies.json")


def load_vendors() -> list[dict[str, Any]]:
    """Return all vendor records."""
    return _load_json("vendors.json")


def load_budgets() -> list[dict[str, Any]]:
    """Return all budget records."""
    return _load_json("budgets.json")
