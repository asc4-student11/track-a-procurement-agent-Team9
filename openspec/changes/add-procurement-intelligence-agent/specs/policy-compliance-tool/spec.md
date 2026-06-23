## ADDED Requirements

### Requirement: Full policy evaluation
The system MUST provide a `check_policy_compliance` tool that evaluates a purchase request against all eight policies in `mock_data/policies.json` through loader-provided data.

Tool contract:

- **Input MUST include**: a complete `PurchaseRequest` object.
- **Return shape MUST include**: `violations` (array), `status` (ok/error), and `message`.
- Each violation object MUST include `policy_id`, `violated_rule`, and `forced_decision`.
- `forced_decision` MUST be either `deny` or `escalate` when a violation is returned.
- **Error behavior MUST include**: structured error output for policy loading/evaluation failures.

#### Scenario: All policies evaluated
- **WHEN** `check_policy_compliance` runs for a valid request
- **THEN** it MUST evaluate the request against all eight policy records before returning

#### Scenario: Violations returned with required fields
- **WHEN** one or more policy rules are violated
- **THEN** each returned violation MUST include `policy_id`, `violated_rule`, and `forced_decision`

#### Scenario: No violations
- **WHEN** no policy is violated
- **THEN** `check_policy_compliance` MUST return an empty `violations` array with `status=ok`

#### Scenario: Policy evaluation error
- **WHEN** policy data cannot be loaded or processed
- **THEN** `check_policy_compliance` MUST return `status=error` and a structured message without unhandled exceptions
