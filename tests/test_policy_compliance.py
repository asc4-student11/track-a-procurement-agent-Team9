"""Policy compliance tool tests for key policy scenarios."""

from __future__ import annotations

import pytest

from data.loader import load_requests
from models import PurchaseRequest
from tools.policy_compliance import check_policy_compliance


def _request_by_id(request_id: str) -> PurchaseRequest:
    """Load one request fixture as a typed model."""
    payload = next(item for item in load_requests() if item["request_id"] == request_id)
    return PurchaseRequest(**payload)


def test_pol004_catering_prohibition_req009_denied() -> None:
    """REQ-009 catering request should be denied under POL-004."""
    req009 = _request_by_id("REQ-009")
    payload = req009.model_dump()
    payload.update({"quantity": 1, "unit_price": 3200.0, "total_amount": 3200.0})
    req009_3200 = PurchaseRequest(**payload)

    result = check_policy_compliance(req009_3200)

    assert result["status"] == "ok"
    violations = {item["policy_id"]: item for item in result["violations"]}
    assert "POL-004" in violations
    assert "violated_rule" in violations["POL-004"]
    assert violations["POL-004"]["violated_rule"]
    assert violations["POL-004"]["forced_decision"] == "deny"


@pytest.mark.parametrize("amount", [10000.0, 49999.0])
def test_pol002_manager_threshold_is_non_forcing(amount: float) -> None:
    """Amounts in manager range are process-only and should not emit POL-002 violations."""
    base_request = _request_by_id("REQ-005")
    payload = base_request.model_dump()
    payload.update(
        {
            "request_id": f"TEST-POL002-{int(amount)}",
            "item_description": "Manager threshold behavior test",
            "quantity": 1,
            "unit_price": amount,
            "total_amount": amount,
        }
    )
    request = PurchaseRequest(**payload)

    result = check_policy_compliance(request)

    assert result["status"] == "ok"
    policy_ids = {item["policy_id"] for item in result["violations"]}
    assert "POL-002" not in policy_ids


def test_pol005_expired_contract_req007_denied() -> None:
    """REQ-007 uses an expired-contract vendor and should be denied under POL-005."""
    req007 = _request_by_id("REQ-007")

    result = check_policy_compliance(req007)

    assert result["status"] == "ok"
    violations = {item["policy_id"]: item for item in result["violations"]}
    assert "POL-005" in violations
    assert "violated_rule" in violations["POL-005"]
    assert violations["POL-005"]["violated_rule"]
    assert violations["POL-005"]["forced_decision"] == "deny"


def test_policy_compliance_no_violations_req001() -> None:
    """REQ-001 should pass policy evaluation without violations."""
    req001 = _request_by_id("REQ-001")

    result = check_policy_compliance(req001)

    assert result["status"] == "ok"
    assert result["violations"] == []
