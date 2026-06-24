"""Budget smoke test using real mock data."""

from __future__ import annotations

from tools.budget import check_budget


def test_check_budget_within_and_over_for_cc003() -> None:
    """Verify within-budget and over-budget behavior for CC-003 (remaining $6,900)."""
    within_result = check_budget("CC-003", 6900.0)
    assert within_result["status"] == "ok"
    assert within_result["within_budget"] is True
    assert within_result["overage"] == 0.0

    over_result = check_budget("CC-003", 11200.0)
    assert over_result["status"] == "ok"
    assert over_result["within_budget"] is False
    assert over_result["overage"] == 4300.0


def test_check_budget_unknown_cost_center_returns_error() -> None:
    """Unknown cost center should return structured error output."""
    result = check_budget("CC-999", 1000.0)

    assert result["status"] == "error"
    assert "Unknown cost center" in result["message"]
