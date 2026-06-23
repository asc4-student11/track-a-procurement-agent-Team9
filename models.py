"""Pydantic v2 models for procurement request input and recommendation output."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class PurchaseRequest(BaseModel):
    """Input schema for a single procurement purchase request."""

    request_id: str
    requestor: str
    cost_center_id: str
    vendor_name: str
    vendor_id: str
    category: str
    item_description: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    total_amount: float = Field(gt=0)
    expected_outcome: Literal["approve", "deny", "escalate", "ambiguous"]
    outcome_reason: str

    @model_validator(mode="after")
    def validate_total_amount(self) -> "PurchaseRequest":
        expected_total = float(self.quantity) * float(self.unit_price)
        if abs(float(self.total_amount) - expected_total) > 0.01:
            raise ValueError("total_amount must match quantity * unit_price within tolerance")
        return self


class ProcurementRecommendation(BaseModel):
    """Structured decision output returned by the procurement agent."""

    decision: Literal["approve", "deny", "escalate"]
    rationale: str

    @field_validator("rationale")
    @classmethod
    def rationale_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("rationale must be non-empty")
        return value
