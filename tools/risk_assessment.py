"""Risk assessment tool for vendor procurement risk signals."""

from __future__ import annotations

from data import loader

_ALLOWED_RISK_LEVELS = {"low", "medium", "high", "critical"}


def _error_result(
    message: str,
    error_type: str,
    risk_level: str = "critical",
) -> dict[str, object]:
    """Return a consistent typed error payload for risk assessment failures."""
    return {
        "status": "error",
        "error_type": error_type,
        "tool": "assess_risk",
        "message": message,
        "compliance_flag": False,
        "contract_status": "unknown",
        "risk_level": risk_level,
    }


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
        vendors = loader.load_vendors()
    except FileNotFoundError as exc:
        return _error_result(f"Vendor data unavailable: {exc}", "file_not_found")
    except KeyError as exc:
        return _error_result(f"Vendor data missing expected field: {exc}", "key_error")
    except Exception as exc:  # pragma: no cover - defensive guardrail
        return _error_result(f"Unexpected vendor data error: {exc}", "unexpected_error")

    vendor = next((item for item in vendors if item.get("vendor_id") == vendor_id), None)
    if vendor is None:
        return _error_result(
            f"Unknown vendor_id: {vendor_id}",
            "validation_error",
            risk_level="high",
        )

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
            **_error_result(
                "Risk computation failed: invalid risk level",
                "validation_error",
                risk_level="critical",
            ),
            "compliance_flag": compliance_flag,
            "contract_status": contract_status,
        }

    return {
        "status": "ok",
        "message": message,
        "compliance_flag": compliance_flag,
        "contract_status": contract_status,
        "risk_level": risk_level,
    }
