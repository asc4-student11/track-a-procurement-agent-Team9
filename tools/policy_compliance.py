"""Policy compliance tool for procurement requests."""

from __future__ import annotations

from data.loader import load_budgets, load_policies, load_vendors
from models import PurchaseRequest


def check_policy_compliance(request: PurchaseRequest) -> dict[str, object]:
    """Evaluate a purchase request against all eight procurement policies.

    The function uses loader-backed policy, vendor, and budget datasets and
    returns only deny/escalate violations in a structured form.

    Args:
        request: Parsed purchase request model.

    Returns:
        A dictionary containing:
        - ``status``: ``"ok"`` when evaluation succeeds, otherwise ``"error"``.
        - ``message``: Human-readable summary of the evaluation outcome.
        - ``violations``: List of violation dictionaries where each entry includes:
                    ``policy_id``, ``violated_rule``, and ``forced_decision``
          (``"deny"`` or ``"escalate"``).
    """
    try:
        policies = load_policies()
        vendors = load_vendors()
        budgets = load_budgets()
    except FileNotFoundError as exc:
        return {
            "status": "error",
            "message": f"Policy data unavailable: {exc}",
            "violations": [],
        }

    policy_by_id = {policy["policy_id"]: policy for policy in policies}
    required_ids = {
        "POL-001",
        "POL-002",
        "POL-003",
        "POL-004",
        "POL-005",
        "POL-006",
        "POL-007",
        "POL-008",
    }
    if set(policy_by_id) != required_ids:
        return {
            "status": "error",
            "message": "Policy dataset must contain exactly POL-001 through POL-008",
            "violations": [],
        }

    vendor = next((v for v in vendors if v.get("vendor_id") == request.vendor_id), None)
    if vendor is None:
        return {
            "status": "error",
            "message": f"Unknown vendor_id: {request.vendor_id}",
            "violations": [],
        }

    budget = next((b for b in budgets if b.get("cost_center_id") == request.cost_center_id), None)
    if budget is None:
        return {
            "status": "error",
            "message": f"Unknown cost_center_id: {request.cost_center_id}",
            "violations": [],
        }

    violations: list[dict[str, str]] = []

    # POL-001: single-source restriction over threshold in contracted categories.
    pol001 = policy_by_id["POL-001"]
    pol001_threshold = float(pol001.get("threshold_amount", 0.0))
    affected_categories = set(pol001.get("affected_categories", []))
    requested_vendor_is_active_contracted = (
        vendor.get("category") == request.category and vendor.get("contract_status") == "active"
    )
    conflicting_active_contracts = [
        v
        for v in vendors
        if v.get("vendor_id") != request.vendor_id
        and v.get("category") == request.category
        and v.get("contract_status") == "active"
    ]
    if (
        request.category in affected_categories
        and request.total_amount > pol001_threshold
        and conflicting_active_contracts
        and not requested_vendor_is_active_contracted
    ):
        violations.append(
            {
                "policy_id": "POL-001",
                "violated_rule": str(pol001["description"]),
                "forced_decision": "deny",
            }
        )

    # POL-002: manager approval threshold; treated as process-only and non-forcing here.
    # This request schema has no explicit approval flag, so no deny/escalate output is emitted.
    _ = policy_by_id["POL-002"]

    # POL-003: director approval threshold.
    pol003 = policy_by_id["POL-003"]
    if request.total_amount >= float(pol003.get("threshold_amount", 0.0)):
        violations.append(
            {
                "policy_id": "POL-003",
                "violated_rule": str(pol003["description"]),
                "forced_decision": "escalate",
            }
        )

    # POL-004: prohibited category (catering).
    pol004 = policy_by_id["POL-004"]
    if request.category in set(pol004.get("affected_categories", [])):
        violations.append(
            {
                "policy_id": "POL-004",
                "violated_rule": str(pol004["description"]),
                "forced_decision": "deny",
            }
        )

    # POL-005: expired contract vendor.
    pol005 = policy_by_id["POL-005"]
    if vendor.get("contract_status") == "expired":
        violations.append(
            {
                "policy_id": "POL-005",
                "violated_rule": str(pol005["description"]),
                "forced_decision": "deny",
            }
        )

    # POL-006: compliance-flagged vendor.
    pol006 = policy_by_id["POL-006"]
    if bool(vendor.get("compliance_flag", False)):
        violations.append(
            {
                "policy_id": "POL-006",
                "violated_rule": str(pol006["description"]),
                "forced_decision": "escalate",
            }
        )

    # POL-007: staffing single-source for engagements above 40 hours.
    pol007 = policy_by_id["POL-007"]
    if (
        request.category in set(pol007.get("affected_categories", []))
        and request.quantity > 40
        and not (vendor.get("contract_status") == "active" and vendor.get("category") == "staffing")
    ):
        violations.append(
            {
                "policy_id": "POL-007",
                "violated_rule": str(pol007["description"]),
                "forced_decision": "deny",
            }
        )

    # POL-008: budget overage prohibition.
    pol008 = policy_by_id["POL-008"]
    if request.total_amount > float(budget.get("remaining", 0.0)):
        violations.append(
            {
                "policy_id": "POL-008",
                "violated_rule": str(pol008["description"]),
                "forced_decision": "deny",
            }
        )

    return {
        "status": "ok",
        "message": "Policy compliance evaluation completed",
        "violations": violations,
    }
