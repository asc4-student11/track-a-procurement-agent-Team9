## ADDED Requirements

### Requirement: Procurement agent input and output contract
The system MUST define `agent.py` orchestration that accepts `PurchaseRequest` input and returns `ProcurementRecommendation` output.

Contract details:

- **Input type MUST be**: `PurchaseRequest` from `models.py`.
- **Output type MUST be**: `ProcurementRecommendation` from `models.py`.
- **Agent construction MUST use**: Pydantic AI `output_type=ProcurementRecommendation`.
- **Output validity MUST enforce**: `decision` limited to `approve`/`deny`/`escalate` and non-empty `rationale`.

#### Scenario: Typed input accepted
- **WHEN** a valid `PurchaseRequest` is provided to the agent orchestration path
- **THEN** evaluation MUST proceed using request fields needed by all four tools

#### Scenario: Typed output produced
- **WHEN** recommendation generation completes
- **THEN** the response MUST conform to `ProcurementRecommendation` and schema validation MUST reject invalid decision values or blank rationale

### Requirement: Four-tool evaluation orchestration
The agent MUST execute all four procurement evaluation tools for standard request evaluation before final decisioning.

Tools in scope:

- `check_budget` (budget tool)
- `check_vendor_duplication` (vendor-duplication tool)
- `check_policy_compliance` (policy-compliance tool)
- `assess_risk` (risk-assessment tool)

Execution requirements:

- **Tool registration MUST include** all four tools in `agent.py` agent workflow.
- **Tool invocation MUST include** all four checks for each valid request.
- **Tool outputs MUST be normalized** into decision findings and rationale evidence.

#### Scenario: Full evaluation path
- **WHEN** a valid request is evaluated
- **THEN** budget, vendor-duplication, policy-compliance, and risk-assessment checks MUST all run before recommendation is finalized

#### Scenario: Tool findings contribute to rationale
- **WHEN** recommendation rationale is composed
- **THEN** rationale MUST reference one or more findings returned by the four tools

### Requirement: Deterministic decision precedence
The agent MUST resolve potentially conflicting tool findings using deterministic priority order.

Priority order:

- `escalate` outranks `deny`
- `deny` outranks `approve`

Decisioning requirements:

- **Final decision MUST be derived** from aggregated findings, not from free-form model choice.
- **Conflict resolution MUST be deterministic** for identical tool outputs.

#### Scenario: Escalate and deny both present
- **WHEN** one or more checks return escalate-class findings and one or more checks return deny-class findings
- **THEN** final `decision` MUST be `escalate`

#### Scenario: Deny without escalate
- **WHEN** one or more checks return deny-class findings and no check returns escalate-class findings
- **THEN** final `decision` MUST be `deny`

#### Scenario: No deny/escalate findings
- **WHEN** all checks complete with no deny-class or escalate-class findings
- **THEN** final `decision` MUST be `approve`

### Requirement: Tool error handling and resilience
The agent MUST surface tool failures in the recommendation rationale and MUST NOT crash or silently ignore failures.

Error-handling requirements:

- **Per-tool execution MUST be isolated** so one tool failure does not prevent remaining tool calls.
- **Unexpected exceptions MUST be converted** to structured error findings.
- **Malformed or unusable tool payloads MUST be treated** as tool failures.
- **Any required tool failure MUST force** final `decision=escalate`.
- **Rationale MUST include** the failing tool name and failure message.

#### Scenario: Single tool failure
- **WHEN** one required tool returns `status=error` or raises an exception
- **THEN** agent evaluation MUST continue running remaining tools and final recommendation MUST be `escalate` with failure reflected in rationale

#### Scenario: Multiple tool failures
- **WHEN** multiple required tools fail
- **THEN** final recommendation MUST be `escalate` and rationale MUST list each failure in structured, human-readable form

### Requirement: System prompt constraints for procurement agent
The system prompt in `agent.py` MUST constrain model behavior to structured procurement recommendation support and must not replace deterministic policy logic.

Prompt constraints:

- **Prompt MUST instruct** the model to produce only `ProcurementRecommendation`-compatible output.
- **Prompt MUST constrain** decision values to `approve`/`deny`/`escalate`.
- **Prompt MUST require** non-empty rationale grounded in tool findings.
- **Prompt MUST state** that all four tools are required checks.
- **Prompt MUST state** deterministic precedence `escalate > deny > approve`.
- **Prompt MUST require** tool errors to be explicitly reflected in rationale.

#### Scenario: Prompt-guided structured output
- **WHEN** the model generates recommendation content
- **THEN** generated content MUST remain compatible with `ProcurementRecommendation` schema and include finding-based rationale text

#### Scenario: Prompt and deterministic reducer alignment
- **WHEN** model-generated text conflicts with deterministic decision reducer outcome
- **THEN** final emitted recommendation MUST follow deterministic reducer precedence and error-handling rules
