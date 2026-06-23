## ADDED Requirements

### Requirement: Dedicated tool specifications
The evaluation tool suite MUST be defined through dedicated capability specs for each tool:

- `budget-tool`
- `vendor-duplication-tool`
- `policy-compliance-tool`
- `risk-assessment-tool`

#### Scenario: Dedicated specs present
- **WHEN** the change specification is reviewed
- **THEN** each of the four tools MUST have its own spec file defining inputs, return shape, scenarios, and error behavior

### Requirement: All tools execute for standard evaluation
The agent MUST call all four tools for standard purchase-request evaluation.

#### Scenario: Full evaluation path
- **WHEN** a valid request is evaluated
- **THEN** the agent MUST run budget, vendor-duplication, policy-compliance, and risk-assessment checks before final decisioning

### Requirement: Loader-only data access
All evaluation tools MUST access domain data through `data/loader.py` and MUST NOT read `mock_data/` files directly.

#### Scenario: Tool data access path
- **WHEN** any tool loads request-related reference data
- **THEN** the tool MUST call loader APIs instead of performing direct JSON file reads

### Requirement: Tool error contract
All evaluation tools MUST return structured error information when failures occur.

#### Scenario: Structured tool failure
- **WHEN** a tool encounters an exception or missing reference data
- **THEN** the tool MUST return a structured error payload usable by agent rationale generation

#### Scenario: Error payload consistency
- **WHEN** any tool returns an error
- **THEN** the payload MUST include at least `status`, `message`, and tool-specific context fields needed for recommendation rationale
