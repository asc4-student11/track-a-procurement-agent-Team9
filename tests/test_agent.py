"""Integration tests for deterministic root agent orchestration."""

from __future__ import annotations

from agent import evaluate_request
from data.loader import load_requests
from models import PurchaseRequest


def _request_by_id(request_id: str) -> PurchaseRequest:
    payload = next(item for item in load_requests() if item["request_id"] == request_id)
    return PurchaseRequest(**payload)


def test_agent_approve_case_req001() -> None:
    result = evaluate_request(_request_by_id("REQ-001"))

    assert result.decision == "approve"
    assert result.rationale.strip()


def test_agent_deny_case_req006() -> None:
    result = evaluate_request(_request_by_id("REQ-006"))

    assert result.decision == "deny"
    assert "budget" in result.rationale.lower()


def test_agent_escalate_case_req011() -> None:
    result = evaluate_request(_request_by_id("REQ-011"))

    assert result.decision == "escalate"
    assert "POL-006" in result.rationale or "compliance" in result.rationale.lower()


def test_agent_near_threshold_escalates_req014() -> None:
    result = evaluate_request(_request_by_id("REQ-014"))

    assert result.decision == "escalate"
    assert "5%" in result.rationale


def test_agent_ambiguous_case_escalates_req015() -> None:
    result = evaluate_request(_request_by_id("REQ-015"))

    assert result.decision == "escalate"
    assert "ambiguous" in result.rationale.lower()


def test_agent_precedence_escalate_over_deny_req010() -> None:
    result = evaluate_request(_request_by_id("REQ-010"))

    assert result.decision == "escalate"
