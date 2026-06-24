"""Main procurement agent orchestration and recommendation helpers."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from pydantic_ai import Agent

from models import ProcurementRecommendation, PurchaseRequest
from tools.budget import check_budget
from tools.policy_compliance import check_policy_compliance
from tools.risk_assessment import assess_risk
from tools.vendor_duplication import check_vendor_duplication

load_dotenv()

DIRECTOR_THRESHOLD = 50_000.0
NEAR_THRESHOLD_RATIO = 0.95

agent: Agent[None, ProcurementRecommendation] = Agent(
    os.getenv("PROCUREMENT_AGENT_MODEL", "openai:gpt-4o-mini"),
    output_type=ProcurementRecommendation,
    system_prompt=(
        "You are the Procurement Intelligence Agent. "
        "Return a ProcurementRecommendation with decision in approve/deny/escalate "
        "and a non-empty rationale."
    ),
)


def evaluate_request(request: PurchaseRequest) -> ProcurementRecommendation:
    """Run all procurement checks and return a deterministic recommendation.

    Decision precedence is always: escalate > deny > approve.
    """
    budget_result = check_budget(request.cost_center_id, request.total_amount)
    vendor_result = check_vendor_duplication(request.vendor_id, request.category, request.total_amount)
    policy_result = check_policy_compliance(request)
    risk_result = assess_risk(request.vendor_id)

    errors: list[str] = []
    escalate_reasons: list[str] = []
    deny_reasons: list[str] = []

    if budget_result.get("status") == "error":
        errors.append(f"budget check error: {budget_result.get('message', 'unknown')}" )
    if vendor_result.get("status") == "error":
        errors.append(f"vendor duplication error: {vendor_result.get('message', 'unknown')}" )
    if policy_result.get("status") == "error":
        errors.append(f"policy compliance error: {policy_result.get('message', 'unknown')}" )
    if risk_result.get("status") == "error":
        errors.append(f"risk assessment error: {risk_result.get('message', 'unknown')}" )

    if errors:
        rationale = (
            "Escalated due to unresolved evaluation errors: "
            + "; ".join(errors)
            + "."
        )
        return ProcurementRecommendation(decision="escalate", rationale=rationale)

    if request.expected_outcome == "ambiguous":
        escalate_reasons.append(
            "request is marked ambiguous in source data and requires manual review"
        )

    if request.total_amount >= DIRECTOR_THRESHOLD * NEAR_THRESHOLD_RATIO:
        escalate_reasons.append(
            f"amount ${request.total_amount:,.2f} is within 5% of ${DIRECTOR_THRESHOLD:,.2f}"
        )

    if bool(risk_result.get("compliance_flag", False)):
        escalate_reasons.append("vendor has active compliance flags (risk assessment)")

    if str(risk_result.get("risk_level")) == "high":
        deny_reasons.append("vendor risk is high due to contract status")

    budget_overage = float(budget_result.get("overage", 0.0))
    if bool(budget_result.get("within_budget", False)) is False:
        deny_reasons.append(f"budget overage of ${budget_overage:,.2f}")

    if vendor_result.get("forced_decision") == "deny":
        deny_reasons.append("POL-001 single-source restriction triggered")

    violations = policy_result.get("violations", [])
    if isinstance(violations, list):
        for item in violations:
            policy_id = str(item.get("policy_id", "unknown"))
            forced_decision = str(item.get("forced_decision", ""))
            if forced_decision == "escalate":
                escalate_reasons.append(f"{policy_id} requires escalation")
            elif forced_decision == "deny":
                deny_reasons.append(f"{policy_id} requires denial")

    if escalate_reasons:
        decision = "escalate"
        rationale = (
            "Escalated after running budget, vendor duplication, policy compliance, and risk checks: "
            + "; ".join(escalate_reasons)
            + "."
        )
    elif deny_reasons:
        decision = "deny"
        rationale = (
            "Denied after running budget, vendor duplication, policy compliance, and risk checks: "
            + "; ".join(deny_reasons)
            + "."
        )
    else:
        decision = "approve"
        remaining = float(budget_result.get("remaining_budget", 0.0))
        rationale = (
            "Approved after running budget, vendor duplication, policy compliance, and risk checks: "
            f"within budget with ${remaining:,.2f} remaining, no deny/escalate policy findings, "
            "and no high-risk vendor signal."
        )

    return ProcurementRecommendation(decision=decision, rationale=rationale)
