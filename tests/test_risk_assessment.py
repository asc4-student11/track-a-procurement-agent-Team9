"""Risk assessment tool tests."""

from __future__ import annotations

from tools.risk_assessment import assess_risk


def test_assess_risk_compliance_flagged_vendor_returns_critical() -> None:
    """V-006 has a compliance flag and should return critical risk."""
    result = assess_risk("V-006")

    assert result["status"] == "ok"
    assert result["compliance_flag"] is True
    assert result["risk_level"] == "critical"


def test_assess_risk_expired_contract_vendor_returns_high() -> None:
    """V-010 has expired contract and should return high risk."""
    result = assess_risk("V-010")

    assert result["status"] == "ok"
    assert result["contract_status"] == "expired"
    assert result["risk_level"] == "high"


def test_assess_risk_returns_enum_risk_level() -> None:
    """Risk level must always be one of the required enum values."""
    result = assess_risk("V-002")

    assert result["status"] == "ok"
    assert result["risk_level"] in {"low", "medium", "high", "critical"}


def test_assess_risk_unknown_vendor_returns_structured_error() -> None:
    """Unknown vendor_id should return structured error output."""
    result = assess_risk("V-999")

    assert result["status"] == "error"
    assert "Unknown vendor_id" in result["message"]
    assert result["risk_level"] in {"low", "medium", "high", "critical"}
