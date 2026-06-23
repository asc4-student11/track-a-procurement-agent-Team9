## ADDED Requirements

### Requirement: Budget check contract
The system MUST provide a `check_budget` tool that evaluates request amount against the remaining budget of the request cost center.

Tool contract:

- **Inputs MUST include**: `cost_center_id`, `total_amount`.
- **Return shape MUST include**: `within_budget` (bool), `remaining_budget` (number), `overage` (number), `status` (ok/error), and `message`.
- **Error behavior MUST include**: structured error for unknown cost center or missing numeric data.

#### Scenario: Budget check within limit
- **WHEN** request `total_amount` is less than or equal to cost center `remaining`
- **THEN** `check_budget` MUST return structured output indicating within-budget status and remaining amount

#### Scenario: Budget check overage
- **WHEN** request `total_amount` exceeds cost center `remaining`
- **THEN** `check_budget` MUST return structured output including overage amount and a deny-class finding

#### Scenario: Budget check unknown cost center
- **WHEN** `cost_center_id` does not exist in loader data
- **THEN** `check_budget` MUST return `status=error` with a structured error message and no unhandled exception
