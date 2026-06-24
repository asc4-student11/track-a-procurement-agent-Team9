"""Budget evaluation tool for procurement requests."""

from __future__ import annotations

from data import loader


def _error_result(message: str, error_type: str) -> dict[str, object]:
    """Return a consistent typed error payload for budget failures."""
    return {
        "status": "error",
        "error_type": error_type,
        "tool": "check_budget",
        "message": message,
        "within_budget": False,
        "remaining_budget": 0.0,
        "overage": 0.0,
    }


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
        return _error_result(
            "requested_amount must be greater than zero",
            "validation_error",
        )

    try:
        budgets = loader.load_budgets()
    except FileNotFoundError as exc:
        return _error_result(f"Budget data unavailable: {exc}", "file_not_found")
    except KeyError as exc:
        return _error_result(f"Budget data missing expected field: {exc}", "key_error")
    except Exception as exc:  # pragma: no cover - defensive guardrail
        return _error_result(f"Unexpected budget data error: {exc}", "unexpected_error")

    record = next((item for item in budgets if item.get("cost_center_id") == cost_center_id), None)

    if record is None:
        return {
            **_error_result(f"Unknown cost center: {cost_center_id}", "validation_error"),
            "overage": round(float(requested_amount), 2),
        }

    try:
        remaining_budget = float(record["remaining"])
    except KeyError as exc:
        return _error_result(f"Budget record missing expected field: {exc}", "key_error")
    except Exception as exc:  # pragma: no cover - defensive guardrail
        return _error_result(f"Unexpected budget record error: {exc}", "unexpected_error")

    overage = max(0.0, float(requested_amount) - remaining_budget)

    return {
        "status": "ok",
        "message": "Budget check completed",
        "within_budget": overage == 0.0,
        "remaining_budget": round(remaining_budget, 2),
        "overage": round(overage, 2),
    }
