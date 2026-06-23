## ADDED Requirements

### Requirement: Vendor risk profile
The system MUST provide an `assess_risk` tool that returns a vendor risk profile for a given vendor ID.

Tool contract:

- **Input MUST include**: `vendor_id`.
- **Return shape MUST include**: `compliance_flag` (bool), `contract_status` (string), `risk_level` (`low`/`medium`/`high`/`critical`), `status` (ok/error), and `message`.
- **Error behavior MUST include**: structured error output when vendor lookup fails.

#### Scenario: Compliance-flagged vendor
- **WHEN** vendor `compliance_flag` is true
- **THEN** `assess_risk` MUST return `compliance_flag=true` and a risk profile consistent with escalate-class handling

#### Scenario: Expired contract vendor
- **WHEN** vendor `contract_status` is `expired`
- **THEN** `assess_risk` MUST return `contract_status=expired` and a risk profile consistent with deny-class handling

#### Scenario: Computed risk level enum
- **WHEN** risk profile is returned
- **THEN** `risk_level` MUST be one of `low`, `medium`, `high`, or `critical`

#### Scenario: Unknown vendor
- **WHEN** `vendor_id` does not exist
- **THEN** `assess_risk` MUST return `status=error` and a structured message without unhandled exceptions
