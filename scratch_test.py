"""Temporary local smoke test. Delete before Session 4."""

from __future__ import annotations

import asyncio
import os

from agent import agent, evaluate_request
from models import PurchaseRequest

# REQ-001: straightforward approve
req = PurchaseRequest(
    request_id="REQ-001",
    requestor="j.smith@fedex.com",
    cost_center_id="CC-001",
    vendor_name="Staples",
    vendor_id="V-002",
    category="office_supplies",
    item_description="Standard office paper and toner",
    quantity=10,
    unit_price=125.0,
    total_amount=1250.0,
    expected_outcome="approve",
    outcome_reason="Within budget and compliant vendor",
)


async def main() -> None:
    # Deterministic local path (no external model call required).
    deterministic = evaluate_request(req)
    print("deterministic:", deterministic.model_dump())

    # Optional LLM path if OPENAI_API_KEY is configured.
    if os.getenv("OPENAI_API_KEY"):
        prompt = (
            "Evaluate this purchase request and return ProcurementRecommendation: "
            f"{req.model_dump_json()}"
        )
        try:
            result = await agent.run(prompt)
            print("llm:", result.output.model_dump())
        except Exception as exc:  # pragma: no cover - scratch-only behavior
            print("llm call failed:", exc)


if __name__ == "__main__":
    asyncio.run(main())
