"""Tests for data loader helpers."""

from __future__ import annotations

from data.loader import load_budgets, load_policies, load_requests, load_vendors


def test_load_requests_returns_all_records() -> None:
    requests = load_requests()
    assert len(requests) == 15
    assert requests[0]["request_id"].startswith("REQ-")


def test_load_policies_returns_eight_policies() -> None:
    policies = load_policies()
    assert len(policies) == 8
    assert {p["policy_id"] for p in policies} >= {"POL-001", "POL-008"}


def test_load_vendors_contains_flagged_vendor() -> None:
    vendors = load_vendors()
    flagged = [v for v in vendors if v["compliance_flag"] is True]
    assert len(flagged) == 1
    assert flagged[0]["vendor_id"] == "V-006"


def test_load_budgets_contains_cc003_remaining() -> None:
    budgets = load_budgets()
    cc003 = next(item for item in budgets if item["cost_center_id"] == "CC-003")
    assert float(cc003["remaining"]) == 6900.0
