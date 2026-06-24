"""Vendor duplication tool test cases."""

from __future__ import annotations

from tools.vendor_duplication import check_vendor_duplication


def test_req_008_vendor_duplication_conflicts() -> None:
    """REQ-008 should detect active office_supplies conflicts V-001 and V-003."""
    result = check_vendor_duplication("V-012", "office_supplies", 28500.0)

    assert result["status"] == "ok"
    assert result["has_conflict"] is True
    assert result["policy_id"] == "POL-001"
    assert result["forced_decision"] == "deny"

    conflict_ids = set(result["conflicting_vendor_ids"])
    assert conflict_ids == {"V-001", "V-003"}


def test_vendor_duplication_no_conflict_for_active_vendor() -> None:
    """Contracted vendor in category should not produce a conflict finding."""
    result = check_vendor_duplication("V-007", "facilities", 8500.0)

    assert result["status"] == "ok"
    assert result["has_conflict"] is False
    assert result["conflicting_vendor_ids"] == []


def test_vendor_duplication_unknown_vendor_returns_error() -> None:
    """Unknown vendor should return structured error output."""
    result = check_vendor_duplication("V-999", "office_supplies", 1000.0)

    assert result["status"] == "error"
    assert "Unknown vendor_id" in result["message"]
