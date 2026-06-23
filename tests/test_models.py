"""Tests for procurement Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from models import ProcurementRecommendation, PurchaseRequest


def test_purchase_request_accepts_valid_record() -> None:
    request = PurchaseRequest(
        request_id="REQ-001",
        requestor="M. Okonkwo",
        cost_center_id="CC-001",
        vendor_name="BlueSky Cloud Solutions",
        vendor_id="V-002",
        category="software_licenses",
        item_description="License renewal",
        quantity=500,
        unit_price=48.0,
        total_amount=24000.0,
        expected_outcome="approve",
        outcome_reason="Valid baseline request",
    )
    assert request.request_id == "REQ-001"


def test_purchase_request_rejects_mismatched_total_amount() -> None:
    with pytest.raises(ValidationError):
        PurchaseRequest(
            request_id="REQ-X",
            requestor="A",
            cost_center_id="CC-001",
            vendor_name="Vendor",
            vendor_id="V-001",
            category="office_supplies",
            item_description="Test",
            quantity=2,
            unit_price=10.0,
            total_amount=25.0,
            expected_outcome="approve",
            outcome_reason="Mismatch",
        )


def test_procurement_recommendation_rejects_empty_rationale() -> None:
    with pytest.raises(ValidationError):
        ProcurementRecommendation(decision="approve", rationale="   ")


def test_procurement_recommendation_rejects_invalid_decision() -> None:
    with pytest.raises(ValidationError):
        ProcurementRecommendation(decision="maybe", rationale="Invalid")
