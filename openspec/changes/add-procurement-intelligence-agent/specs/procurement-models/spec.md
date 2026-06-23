## ADDED Requirements

### Requirement: PurchaseRequest schema coverage
The system MUST define a `PurchaseRequest` schema that represents every field present in `mock_data/requests.json`.

The schema MUST include these fields:

- `request_id`
- `requestor`
- `cost_center_id`
- `vendor_name`
- `vendor_id`
- `category`
- `item_description`
- `quantity`
- `unit_price`
- `total_amount`
- `expected_outcome`
- `outcome_reason`

#### Scenario: All request fields represented
- **WHEN** a request record is loaded from the project request dataset
- **THEN** every dataset field listed above MUST map to a corresponding `PurchaseRequest` schema field

### Requirement: PurchaseRequest numeric validation
The `PurchaseRequest` schema MUST include Pydantic validators for numeric data integrity.

Validation rules:

- `quantity` MUST be an integer greater than 0.
- `unit_price` MUST be greater than 0.
- `total_amount` MUST be greater than 0.
- `total_amount` SHOULD equal `quantity * unit_price` within a defined decimal tolerance.

#### Scenario: Invalid numeric input is rejected
- **WHEN** `quantity` is non-integer or less than 1, or `unit_price`/`total_amount` is less than or equal to 0
- **THEN** model validation MUST reject the input with a structured validation error

#### Scenario: Amount consistency check
- **WHEN** `total_amount` materially differs from `quantity * unit_price`
- **THEN** validation SHOULD fail with a clear amount-mismatch error message

### Requirement: ProcurementRecommendation output schema
The system MUST define a `ProcurementRecommendation` schema for all final recommendations.

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
