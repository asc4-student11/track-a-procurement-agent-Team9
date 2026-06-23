## Context

The procurement capstone requires a deterministic pre-screening agent that evaluates purchase requests and returns structured recommendations for analyst review. Current behavior is manually interpreted from request, vendor, policy, and budget data, which creates inconsistent outcomes and weak traceability.

The project already defines data fixtures under `mock_data/`, project constraints under `.github/copilot-instructions.md`, and target modules under `agent.py`, `models.py`, `tools/`, and `data/loader.py`. Design must preserve these constraints:

- Structured output through Pydantic AI with `output_type=ProcurementRecommendation`.
- Input/output validation through Pydantic v2 models.
- Data access through `data/loader.py` only.
- Deterministic outcome priority: `escalate > deny > approve`.
- Tool failures surfaced in rationale (no silent ignore).

## Goals / Non-Goals

**Goals:**

- Define a stable decision pipeline using four checks: budget, vendor duplication, policy compliance, and risk assessment.
- Ensure recommendation output is always schema-valid with allowed decision values and non-empty rationale.
- Define explicit conflict resolution so mixed signals always produce a deterministic decision.
- Ensure failure-safe behavior where tool errors are captured and reflected in recommendation rationale.

**Non-Goals:**

- Building UI, workflow orchestration, or approval screens.
- Adding deployment, authentication, database persistence, or external integrations.
- Changing source mock data files.

## Decisions

### Decision 1: Enforce structured output contract at runtime

The agent will be configured with `output_type=ProcurementRecommendation` so model outputs are constrained and validated.

Alternatives considered:

- Manual JSON parsing and post-validation. Rejected because it is less reliable and increases parsing failure paths.
- Free-form text responses. Rejected because it cannot guarantee contract compliance.

### Decision 2: Use a tool-first evaluation pipeline

Recommendation generation will depend on four tool calls:

1. `check_budget`
2. `check_vendor_duplication`
3. `check_policy_compliance`
4. `assess_risk`

Each tool returns structured data with explicit status and findings for rationale composition.

Tool selection logic:

- The agent MUST execute all four tools for each request in this order: `check_budget`, `check_vendor_duplication`, `check_policy_compliance`, `assess_risk`.
- Tool execution is based on request and vendor context loaded through `data/loader.py`; tools are not optional for standard request processing.
- If a required input for a tool is unavailable, the tool still returns a structured error payload rather than being skipped silently.

Alternatives considered:

- Monolithic agent prompt with no tools. Rejected due to weak traceability and testability.
- Partial tooling with inline data logic in agent. Rejected due to poor separation of concerns.

### Decision 3: Deterministic precedence for conflicting results

When checks disagree, precedence is fixed as `escalate > deny > approve`.

Examples:

- Any escalate condition plus deny condition results in `escalate`.
- Deny with no escalate condition results in `deny`.
- Approve requires absence of both escalate and deny conditions.

Alternatives considered:

- Deny-over-escalate strategy. Rejected to preserve conservative governance handling for high-uncertainty/high-risk scenarios.

### Decision 4: Loader-only data access

Tool modules and agent logic read domain data via `data/loader.py` abstraction.

Alternatives considered:

- Direct JSON reads in each tool. Rejected because it duplicates logic and violates project convention.

### Decision 5: Failure-safe recommendation behavior

Tool exceptions, unavailable data, or parse failures do not crash recommendation generation. Failures are captured in rationale and produce `escalate` when uncertainty remains unresolved.

Fallback path:

1. Execute each required tool and capture either structured findings or structured error output.
2. Aggregate findings and errors into a single decision context.
3. If any unresolved error affects decision confidence, set final decision to `escalate`.
4. Include each relevant failure in the final rationale text.
5. Return schema-valid `ProcurementRecommendation` output even on partial failure.

Alternatives considered:

- Raise terminal exception to caller. Rejected because business flow needs an actionable recommendation object.

## Risks / Trade-offs

- [Risk] Divergent interpretation of ambiguous sample request behavior (REQ-015) -> Mitigation: codify precedence and fallback behavior explicitly in spec scenarios and tests.
- [Risk] Policy threshold edge behavior (for example near-director threshold escalation) may be inconsistently implemented -> Mitigation: define exact scenario criteria in specs and integration tests.
- [Risk] Tool-level schema drift could break final rationale composition -> Mitigation: use typed models for tool outputs and enforce tests per tool primary success path.
- [Risk] Over-escalation may reduce operational efficiency -> Mitigation: track escalation reasons in rationale and refine rules only via spec updates.
