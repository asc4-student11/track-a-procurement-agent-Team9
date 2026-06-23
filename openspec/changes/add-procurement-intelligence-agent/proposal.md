## Why

FedEx procurement teams need a reliable pre-screen that can consistently evaluate purchase requests and produce explainable recommendations before analyst review. The current process is manual and inconsistent, creating variability in outcomes and rationale quality.

This change defines a deterministic, schema-validated recommendation workflow for the capstone so implementation teams can build against one clear contract.

## What Changes

- Introduce a Pydantic AI procurement agent that evaluates each purchase request and returns a structured recommendation.
- Define strict input and output contracts using Pydantic v2 models:
  - `PurchaseRequest` for request ingestion.
  - `ProcurementRecommendation` with `decision` constrained to `approve`, `deny`, or `escalate`, and a required non-empty `rationale`.
- Add four tool-driven evaluation checks:
  - `check_budget`
  - `check_vendor_duplication`
  - `check_policy_compliance`
  - `assess_risk`
- Require the agent to load mock data through `data/loader.py` only (no direct reads from `mock_data/` in tool logic).
- Define deterministic decision precedence as `escalate > deny > approve`.
- Require tool and data failures to be surfaced in recommendation rationale rather than ignored.
- Keep scope limited to core decisioning logic and tests only. Out of scope: deployment, UI, authentication/authorization, and persistent storage.

## Capabilities

### New Capabilities
- `procurement-models`: Defines `PurchaseRequest` and `ProcurementRecommendation` schema contracts, including field coverage and validators.
- `procurement-recommendation-contract`: Defines structured output behavior, allowed decision values, rationale requirements, and deterministic conflict resolution.
- `procurement-evaluation-tools`: Defines shared cross-tool behavior (full tool execution, loader-only data access, and consistent error contracts).
- `budget-tool`: Defines the `check_budget` input contract, output shape, and overage/error scenarios.
- `vendor-duplication-tool`: Defines the `check_vendor_duplication` input contract, output shape, and POL-001 threshold deny behavior.
- `policy-compliance-tool`: Defines the `check_policy_compliance` requirement to evaluate all eight policies and return violation details.
- `risk-assessment-tool`: Defines the `assess_risk` input contract and risk profile output (`low`/`medium`/`high`/`critical`).

### Modified Capabilities
- None.

## Impact

- Affected code: `agent.py`, `models.py`, `tools/*.py`, `data/loader.py`, and tests under `tests/`.
- Affected behavior: Procurement recommendations become deterministic and schema-validated.
- Affected process: OpenSpec artifacts and tests become the source of truth for implementation readiness.
- Dependencies: Continued use of `pydantic-ai`, `pydantic`, and `pytest` stack already defined in project configuration.

## Risks

- Ambiguous sample behavior (for example REQ-015) can lead to inconsistent implementations if precedence and fallback rules are not explicit.
- Policy threshold edge interpretation (such as near-threshold escalation) may diverge unless scenarios are specified precisely in specs.
- Tool or loader failures can degrade recommendation quality if error handling is not surfaced clearly in rationale.
