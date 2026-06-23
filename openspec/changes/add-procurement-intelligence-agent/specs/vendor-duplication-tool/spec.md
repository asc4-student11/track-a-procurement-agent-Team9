## ADDED Requirements

### Requirement: Vendor duplication detection
The system MUST provide a `check_vendor_duplication` tool that determines whether a purchase request references a vendor while another active contract already exists in the same category.

Tool contract:

- **Inputs MUST include**: `vendor_id`, `category`, and `total_amount`.
- **Return shape MUST include**: `has_conflict` (bool), `conflicting_vendor_ids` (array), `conflicting_contract_details` (array), `policy_id` (string or null), `threshold_applied` (number or null), `forced_decision` (`deny`/null), `status` (ok/error), and `message`.
- `conflicting_contract_details` MUST include, for each conflicting vendor, at least `vendor_id`, `contract_id`, and `contract_status`.
- **Error behavior MUST include**: structured error output for missing vendor/category reference data.

#### Scenario: Active same-category contract conflict exists
- **WHEN** request category has one or more active contracts with vendors other than the requested vendor
- **THEN** `check_vendor_duplication` MUST return `has_conflict=true` and include `conflicting_vendor_ids` with matching `conflicting_contract_details`

#### Scenario: POL-001 deny threshold reached
- **WHEN** `has_conflict=true` and request `total_amount` is greater than 25000 (POL-001 threshold)
- **THEN** `check_vendor_duplication` MUST return `policy_id=POL-001`, `threshold_applied=25000`, and `forced_decision=deny`

#### Scenario: No conflict
- **WHEN** requested vendor is contracted for the category or no active same-category contracts exist
- **THEN** `check_vendor_duplication` MUST return `has_conflict=false` with empty conflict arrays

#### Scenario: Reference data error
- **WHEN** vendor/category lookup fails
- **THEN** `check_vendor_duplication` MUST return `status=error` and a structured message without throwing an unhandled exception
