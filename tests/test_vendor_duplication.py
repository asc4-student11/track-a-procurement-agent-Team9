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
