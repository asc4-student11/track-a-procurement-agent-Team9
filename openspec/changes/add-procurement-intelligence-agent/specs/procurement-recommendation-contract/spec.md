## ADDED Requirements

### Requirement: Recommendation output schema
The system MUST return a `ProcurementRecommendation` object for every processed request.

#### Scenario: Schema-constrained output
- **WHEN** the agent completes recommendation generation
- **THEN** the response MUST conform to `ProcurementRecommendation` via `output_type`

### Requirement: Allowed decision values
`ProcurementRecommendation.decision` MUST be limited to `approve`, `deny`, or `escalate`.

#### Scenario: Invalid decision is rejected
- **WHEN** a generated output contains any decision value outside `approve`, `deny`, `escalate`
- **THEN** schema validation MUST reject the output as invalid

### Requirement: Non-empty rationale
`ProcurementRecommendation.rationale` MUST be present and non-empty.

#### Scenario: Rationale contains findings
- **WHEN** the agent returns a decision
- **THEN** rationale MUST include at least one non-whitespace character and reference at least one check finding

#### Scenario: Empty rationale is rejected
- **WHEN** a generated recommendation has missing, empty, or whitespace-only rationale
- **THEN** schema validation MUST reject the output

### Requirement: Deterministic decision precedence
Recommendation conflict resolution MUST apply precedence in this order: `escalate > deny > approve`.

#### Scenario: Escalate outranks deny
- **WHEN** one or more checks indicate `escalate` and one or more checks indicate `deny`
- **THEN** the final decision MUST be `escalate`

#### Scenario: Deny outranks approve
- **WHEN** checks indicate `deny` and no check indicates `escalate`
- **THEN** the final decision MUST be `deny`

### Requirement: Tool error reflection
Tool failures MUST be surfaced in rationale and MUST NOT be silently ignored.

#### Scenario: Tool error fallback
- **WHEN** any required tool fails or returns unusable data
- **THEN** rationale MUST include the failure and final decision MUST default to `escalate`
