"""Budget evaluation tool for procurement requests."""

from __future__ import annotations

from data.loader import load_budgets


def check_budget(cost_center_id: str, requested_amount: float) -> dict[str, object]:
    """Evaluate whether a request amount is within a cost center's remaining budget.

    The function reads budget records through ``data.loader.load_budgets`` and returns
    a structured response for both success and error paths.

    Args:
        cost_center_id: Cost center identifier from the purchase request.
        requested_amount: Requested total purchase amount in USD.

    Returns:
        A dictionary with these keys:
        - ``status``: ``"ok"`` for successful evaluation, otherwise ``"error"``.
        - ``message``: Human-readable summary of evaluation result.
        - ``within_budget``: Whether the request is within remaining budget.
        - ``remaining_budget``: Remaining budget for the cost center in USD.
        - ``overage``: Positive over-budget amount in USD, else ``0.0``.
    """
    if requested_amount <= 0:
        return {
            "status": "error",
            "message": "requested_amount must be greater than zero",
            "within_budget": False,
            "remaining_budget": 0.0,
            "overage": 0.0,
        }

    budgets = load_budgets()
    record = next((item for item in budgets if item.get("cost_center_id") == cost_center_id), None)

    if record is None:
        return {
            "status": "error",
            "message": f"Unknown cost center: {cost_center_id}",
            "within_budget": False,
            "remaining_budget": 0.0,
            "overage": round(float(requested_amount), 2),
        }

    remaining_budget = float(record["remaining"])
    overage = max(0.0, float(requested_amount) - remaining_budget)

    return {
        "status": "ok",
        "message": "Budget check completed",
        "within_budget": overage == 0.0,
        "remaining_budget": round(remaining_budget, 2),
        "overage": round(overage, 2),
    }
