"""Vendor duplication tool for POL-001 single-source checks."""

from __future__ import annotations

from data import loader

POL001_THRESHOLD = 25_000.0


def _error_result(message: str, error_type: str) -> dict[str, object]:
    """Return a consistent typed error payload for vendor duplication failures."""
    return {
        "status": "error",
        "error_type": error_type,
        "tool": "check_vendor_duplication",
        "message": message,
        "has_conflict": False,
        "conflicting_vendor_ids": [],
        "conflicting_contract_details": [],
        "policy_id": None,
        "threshold_applied": None,
        "forced_decision": None,
    }


def check_vendor_duplication(
    vendor_id: str,
    category: str,
    total_amount: float = 0.0,
) -> dict[str, object]:
    """Detect active same-category contract conflicts and apply POL-001 threshold logic.

    This tool checks whether the requested vendor conflicts with other active-contract
    vendors in the same category. POL-001 deny behavior is only triggered when
    ``total_amount`` is greater than 25000 in a category where active conflicting
    contract vendors exist.

    Args:
        vendor_id: Vendor identifier from the purchase request.
        category: Purchase category from the purchase request.
        total_amount: Requested purchase amount in USD.

    Returns:
        Structured result with keys:
        - status: "ok" or "error"
        - message: human-readable summary
        - has_conflict: whether active same-category conflicts exist
        - conflicting_vendor_ids: list of conflicting vendor IDs
        - conflicting_contract_details: list of dicts with vendor_id, contract_id, contract_status
        - policy_id: "POL-001" when threshold-triggered violation exists, else None
        - threshold_applied: 25000 when threshold-triggered violation exists, else None
        - forced_decision: "deny" when threshold-triggered violation exists, else None
    """
    if total_amount < 0:
        return _error_result(
            "total_amount must be greater than or equal to zero",
            "validation_error",
        )

    try:
        vendors = loader.load_vendors()
    except FileNotFoundError as exc:
        return _error_result(f"Vendor data unavailable: {exc}", "file_not_found")
    except KeyError as exc:
        return _error_result(f"Vendor data missing expected field: {exc}", "key_error")
    except Exception as exc:  # pragma: no cover - defensive guardrail
        return _error_result(f"Unexpected vendor data error: {exc}", "unexpected_error")

    requested_vendor = next((v for v in vendors if v.get("vendor_id") == vendor_id), None)
    if requested_vendor is None:
        return _error_result(f"Unknown vendor_id: {vendor_id}", "validation_error")

    requested_vendor_is_active_contracted = (
        requested_vendor.get("category") == category
        and requested_vendor.get("contract_status") == "active"
    )

    conflicts = [
        vendor
        for vendor in vendors
        if vendor.get("vendor_id") != vendor_id
        and vendor.get("category") == category
        and vendor.get("contract_status") == "active"
    ]

    conflicting_vendor_ids = [str(v["vendor_id"]) for v in conflicts]
    conflicting_contract_details = [
        {
            "vendor_id": str(v["vendor_id"]),
            "contract_id": str(v.get("contract_id", "")),
            "contract_status": str(v.get("contract_status", "")),
        }
        for v in conflicts
    ]

    threshold_triggered = (
        bool(conflicts)
        and float(total_amount) > POL001_THRESHOLD
        and not requested_vendor_is_active_contracted
    )
    if threshold_triggered:
        return {
            "status": "ok",
            "message": "POL-001 threshold exceeded with active same-category contract conflicts",
            "has_conflict": True,
            "conflicting_vendor_ids": conflicting_vendor_ids,
            "conflicting_contract_details": conflicting_contract_details,
            "policy_id": "POL-001",
            "threshold_applied": POL001_THRESHOLD,
            "forced_decision": "deny",
        }

    if conflicts:
        return {
            "status": "ok",
            "message": "Active same-category conflicts found, but POL-001 threshold not exceeded",
            "has_conflict": True,
            "conflicting_vendor_ids": conflicting_vendor_ids,
            "conflicting_contract_details": conflicting_contract_details,
            "policy_id": None,
            "threshold_applied": None,
            "forced_decision": None,
        }

    return {
        "status": "ok",
        "message": "No active same-category contract conflicts found",
        "has_conflict": False,
        "conflicting_vendor_ids": [],
        "conflicting_contract_details": [],
        "policy_id": None,
        "threshold_applied": None,
        "forced_decision": None,
    }
