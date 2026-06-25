"""Async test suite for core procurement agent outcomes."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from agent import evaluate_request
from data.loader import load_requests
from models import PurchaseRequest


def _request_by_id(request_id: str) -> PurchaseRequest:
    payload = next(item for item in load_requests() if item["request_id"] == request_id)
    return PurchaseRequest(**payload)


def _run_request(request: PurchaseRequest) -> SimpleNamespace:
    recommendation = evaluate_request(request)
    return SimpleNamespace(data=recommendation)


@pytest.mark.asyncio
async def test_agent_approve_req001() -> None:
    result = _run_request(_request_by_id("REQ-001"))

    assert result.data.decision == "approve"
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_agent_deny_req006_budget_overage() -> None:
    result = _run_request(_request_by_id("REQ-006"))

    assert result.data.decision == "deny"
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_agent_policy_deny_req009_pol004() -> None:
    result = _run_request(_request_by_id("REQ-009"))

    assert result.data.decision == "deny"
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_agent_escalate_req011_compliance_flag() -> None:
    result = _run_request(_request_by_id("REQ-011"))

    assert result.data.decision == "escalate"
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()
