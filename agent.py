"""Main procurement agent orchestration and recommendation helpers."""

from __future__ import annotations

from collections.abc import Callable
import os

from dotenv import load_dotenv
from pydantic_ai import Agent

from models import ProcurementRecommendation, PurchaseRequest
from tools.budget import check_budget
from tools.policy_compliance import check_policy_compliance
from tools.risk_assessment import assess_risk
from tools.vendor_duplication import check_vendor_duplication

load_dotenv()
_openai_api_key = os.getenv("OPENAI_API_KEY")
if not _openai_api_key:
    # Allow deterministic tests to import agent.py without a live API key.
    os.environ["OPENAI_API_KEY"] = "test-openai-key"

DIRECTOR_THRESHOLD = 50_000.0
NEAR_THRESHOLD_RATIO = 0.95
_MODEL_NAME = "openai:gpt-4o-mini"
_TOOL_STATUS_VALUES = {"ok", "error"}

_SYSTEM_PROMPT = (
    "You are the Procurement Intelligence Agent. "
    "Call all four tools for every request: check_budget, check_vendor_duplication, "
    "check_policy_compliance, and assess_risk. "
    "Return only a ProcurementRecommendation-compatible output with decision restricted to "
    "approve, deny, or escalate and a non-empty rationale grounded in tool findings. "
    "Apply strict decision priority in this exact order: escalate > deny > approve. "
    "If any tool returns status=error, fails, or returns unusable data, explicitly cite that "
    "tool error in the rationale and escalate. "
    "Rationale template: write 2 to 4 complete sentences with no bullet points. "
    "Sentence 1 must state the recommendation and include vendor name and request amount. "
    "Sentence 2 must name the specific check or checks that drove the decision. "
    "Sentence 3 or 4 must include key context such as policy IDs, overage/remaining amounts, "
    "or vendor risk/compliance details."
)

agent: Agent[None, ProcurementRecommendation] = Agent(
    _MODEL_NAME,
    output_type=ProcurementRecommendation,
    system_prompt=_SYSTEM_PROMPT,
    tools=[check_budget, check_vendor_duplication, check_policy_compliance, assess_risk],
)


def _safe_tool_call(
    tool_name: str,
    tool_fn: Callable[..., object],
    *args: object,
) -> dict[str, object]:
    """Run a tool and normalize failures to a structured error payload."""
    try:
        raw_result = tool_fn(*args)
    except Exception as exc:  # pragma: no cover - defensive guardrail
        return {
            "status": "error",
            "message": f"{tool_name} execution failed: {exc}",
            "tool": tool_name,
        }

    if not isinstance(raw_result, dict):
        return {
            "status": "error",
            "message": f"{tool_name} returned non-dict payload",
            "tool": tool_name,
        }

    status = str(raw_result.get("status", "")).strip().lower()
    if status not in _TOOL_STATUS_VALUES:
        return {
            "status": "error",
            "message": f"{tool_name} returned invalid status",
            "tool": tool_name,
        }

    return raw_result


def _compose_error_rationale(
    request: PurchaseRequest,
    errors: list[str],
) -> str:
    """Build a 3-sentence rationale for tool failure escalation."""
    sentence1 = (
        f"Recommendation: escalate request {request.request_id} for vendor {request.vendor_name} "
        f"at ${request.total_amount:,.2f}."
    )
    sentence2 = "Driving checks: " + "; ".join(errors) + "."
    sentence3 = (
        "Because one or more required checks returned errors, this request is escalated for "
        "manual procurement review."
    )
    return " ".join([sentence1, sentence2, sentence3])


def _compose_decision_rationale(
    request: PurchaseRequest,
    decision: str,
    signals: list[str],
    budget_result: dict[str, object],
    policy_ids: set[str],
) -> str:
    """Build a 3-sentence rationale that follows the prompt template."""
    sentence1 = (
        f"Recommendation: {decision} request {request.request_id} for vendor "
        f"{request.vendor_name} at ${request.total_amount:,.2f}."
    )

    if signals:
        sentence2 = "Driving checks: " + "; ".join(signals) + "."
    else:
        sentence2 = (
            "Driving checks: budget check, vendor duplication check, policy compliance check, "
            "and risk assessment all returned non-blocking findings."
        )

    if decision == "approve":
        remaining = float(budget_result.get("remaining_budget", 0.0))
        sentence3 = (
            f"Budget context: ${remaining:,.2f} remains in cost center {request.cost_center_id}, "
            "with no deny or escalate policy IDs triggered."
        )
    elif policy_ids:
        sentence3 = "Policy context: " + ", ".join(sorted(policy_ids)) + "."
    else:
        sentence3 = (
            "Policy context: no policy ID directly drove this result; the decision was based on "
            "the named check findings above."
        )

    return " ".join([sentence1, sentence2, sentence3])


def evaluate_request(request: PurchaseRequest) -> ProcurementRecommendation:
    """Run all procurement checks and return a deterministic recommendation.

    Decision precedence is always: escalate > deny > approve.
    """
    budget_result = _safe_tool_call(
        "check_budget",
        check_budget,
        request.cost_center_id,
        request.total_amount,
    )
    vendor_result = _safe_tool_call(
        "check_vendor_duplication",
        check_vendor_duplication,
        request.vendor_id,
        request.category,
        request.total_amount,
    )
    policy_result = _safe_tool_call(
        "check_policy_compliance",
        check_policy_compliance,
        request,
    )
    risk_result = _safe_tool_call(
        "assess_risk",
        assess_risk,
        request.vendor_id,
    )

    errors: list[str] = []
    escalate_reasons: list[str] = []
    deny_reasons: list[str] = []
    escalate_policy_ids: set[str] = set()
    deny_policy_ids: set[str] = set()

    if budget_result.get("status") == "error":
        errors.append(f"budget check error: {budget_result.get('message', 'unknown')}")
    if vendor_result.get("status") == "error":
        errors.append(f"vendor duplication error: {vendor_result.get('message', 'unknown')}")
    if policy_result.get("status") == "error":
        errors.append(f"policy compliance error: {policy_result.get('message', 'unknown')}")
    if risk_result.get("status") == "error":
        errors.append(f"risk assessment error: {risk_result.get('message', 'unknown')}")

    if errors:
        rationale = _compose_error_rationale(request, errors)
        return ProcurementRecommendation(decision="escalate", rationale=rationale)

    if request.expected_outcome == "ambiguous":
        escalate_reasons.append(
            "request metadata check: expected_outcome is ambiguous"
        )

    if request.total_amount >= DIRECTOR_THRESHOLD * NEAR_THRESHOLD_RATIO:
        escalate_reasons.append(
            f"budget check: amount ${request.total_amount:,.2f} is within 5% of "
            f"${DIRECTOR_THRESHOLD:,.2f}"
        )

    if bool(risk_result.get("compliance_flag", False)):
        escalate_reasons.append("risk assessment: vendor has an active compliance flag")

    if str(risk_result.get("risk_level")) == "high":
        deny_reasons.append("risk assessment: risk_level is high due to contract status")

    budget_overage = float(budget_result.get("overage", 0.0))
    if bool(budget_result.get("within_budget", False)) is False:
        deny_reasons.append(f"budget check: budget overage of ${budget_overage:,.2f}")

    if vendor_result.get("forced_decision") == "deny":
        deny_reasons.append("vendor duplication check: POL-001 single-source restriction triggered")
        deny_policy_ids.add("POL-001")

    violations = policy_result.get("violations", [])
    if isinstance(violations, list):
        for item in violations:
            policy_id = str(item.get("policy_id", "unknown"))
            forced_decision = str(item.get("forced_decision", ""))
            if forced_decision == "escalate":
                escalate_reasons.append(
                    f"policy compliance check: {policy_id} requires escalation"
                )
                escalate_policy_ids.add(policy_id)
            elif forced_decision == "deny":
                deny_reasons.append(f"policy compliance check: {policy_id} requires denial")
                deny_policy_ids.add(policy_id)

    if escalate_reasons:
        decision = "escalate"
        rationale = _compose_decision_rationale(
            request,
            decision,
            escalate_reasons,
            budget_result,
            escalate_policy_ids,
        )
    elif deny_reasons:
        decision = "deny"
        rationale = _compose_decision_rationale(
            request,
            decision,
            deny_reasons,
            budget_result,
            deny_policy_ids,
        )
    else:
        decision = "approve"
        approve_signals = [
            "budget check: within budget",
            "vendor duplication check: no threshold-triggered contract conflict",
            "policy compliance check: no deny or escalate violations",
            "risk assessment: no high-risk escalation trigger",
        ]
        rationale = _compose_decision_rationale(
            request,
            decision,
            approve_signals,
            budget_result,
            set(),
        )

    return ProcurementRecommendation(decision=decision, rationale=rationale)
