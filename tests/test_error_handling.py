"""Tests for agent error handling and escalation behavior."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from agent import evaluate_request
from data.loader import load_requests
from models import PurchaseRequest


def _request_by_id(request_id: str) -> PurchaseRequest:
    payload = next(item for item in load_requests() if item["request_id"] == request_id)
    return PurchaseRequest(**payload)


def _run_request(request: PurchaseRequest) -> SimpleNamespace:
    recommendation = evaluate_request(request)
    return SimpleNamespace(data=recommendation)


def test_agent_escalates_when_budget_loader_raises_runtime_error() -> None:
    request = _request_by_id("REQ-001")

    with patch("data.loader.load_budgets", side_effect=RuntimeError("simulated budget failure")):
        result = _run_request(request)

    assert result.data.decision == "escalate"
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()
    assert "budget check error" in result.data.rationale.lower()
    assert "simulated budget failure" in result.data.rationale.lower()


def test_agent_escalates_for_unknown_vendor_id() -> None:
    base_request = _request_by_id("REQ-001")
    request = base_request.model_copy(
        update={
            "vendor_id": "V-999",
            "vendor_name": "Unknown Vendor LLC",
        }
    )

    result = _run_request(request)

    assert result.data.decision == "escalate"
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()
    assert "unknown vendor" in result.data.rationale.lower()
