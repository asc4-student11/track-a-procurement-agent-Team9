"""Risk assessment tool for vendor procurement risk signals."""

from __future__ import annotations

from data.loader import load_vendors

_ALLOWED_RISK_LEVELS = {"low", "medium", "high", "critical"}


def assess_risk(vendor_id: str) -> dict[str, object]:
    """Return a structured vendor risk profile for procurement decisions.

    Args:
        vendor_id: Vendor identifier from a purchase request.

    Returns:
        Dictionary with keys:
        - status: "ok" or "error"
        - message: evaluation summary or error detail
        - compliance_flag: whether vendor has an active compliance hold
        - contract_status: current contract state for the vendor
        - risk_level: one of low/medium/high/critical
    """
    try:
        vendors = load_vendors()
    except FileNotFoundError as exc:
        return {
            "status": "error",
            "message": f"Vendor data unavailable: {exc}",
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "critical",
        }

    vendor = next((item for item in vendors if item.get("vendor_id") == vendor_id), None)
    if vendor is None:
        return {
            "status": "error",
            "message": f"Unknown vendor_id: {vendor_id}",
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "high",
        }

    compliance_flag = bool(vendor.get("compliance_flag", False))
    contract_status = str(vendor.get("contract_status", "none"))

    if compliance_flag:
        risk_level = "critical"
        message = "Vendor has active compliance flags; escalate for legal/compliance review"
    elif contract_status == "expired":
        risk_level = "high"
        message = "Vendor contract is expired; deny until contract is renewed"
    elif contract_status == "none":
        risk_level = "medium"
        message = "Vendor has no contract on file; review required before approval"
    else:
        risk_level = "low"
        message = "Vendor contract is active and no compliance flag is present"

    if risk_level not in _ALLOWED_RISK_LEVELS:
        return {
            "status": "error",
            "message": "Risk computation failed: invalid risk level",
            "compliance_flag": compliance_flag,
            "contract_status": contract_status,
            "risk_level": "critical",
        }

    return {
        "status": "ok",
        "message": message,
        "compliance_flag": compliance_flag,
        "contract_status": contract_status,
        "risk_level": risk_level,
    }
