## 1. Models and schema validators

- [x] 1.1 Define `PurchaseRequest` in `models.py` with all fields present in `mock_data/requests.json`.
- [x] 1.2 Add numeric validators for `quantity`, `unit_price`, and `total_amount` in `PurchaseRequest`.
- [x] 1.3 Define `ProcurementRecommendation` with `decision` constrained to `approve`/`deny`/`escalate`.
- [x] 1.4 Enforce non-empty `rationale` validation in `ProcurementRecommendation`.
- [x] 1.5 Add model tests for valid and invalid `decision` values plus empty-rationale rejection.

## 2. Data loader component

- [x] 2.1 Implement loader functions in `data/loader.py` for requests, budgets, vendors, and policies.
- [x] 2.2 Add structured loader error behavior for missing files or invalid record lookups.
- [x] 2.3 Add loader tests for successful retrieval and primary error paths.

## 3. Budget tool component

- [x] 3.1 Implement `check_budget` in `tools/budget.py` with typed inputs and structured output fields.
- [x] 3.2 Return `within_budget`, `remaining_budget`, and `overage` for valid cost centers.
- [x] 3.3 Return structured error output for unknown cost centers.
- [x] 3.4 Add `tests/test_budget.py` success and error-path coverage.

## 4. Vendor duplication tool component

- [x] 4.1 Implement `check_vendor_duplication` in `tools/vendor_duplication.py` with category and threshold logic.
- [x] 4.2 Return structured conflict details including conflicting vendor IDs and applied policy context.
- [x] 4.3 Add structured error output when vendor/category data is unavailable.
- [x] 4.4 Add `tests/test_vendor_duplication.py` success and error/edge-path coverage.

## 5. Policy compliance tool component

- [x] 5.1 Implement `check_policy_compliance` in `tools/policy_compliance.py` to evaluate all policy records.
- [x] 5.2 Return structured violations including `policy_id`, rule description, and decision effect.
- [x] 5.3 Return explicit no-violation output shape when policies pass.
- [x] 5.4 Add structured error output for policy evaluation failures.
- [x] 5.5 Add `tests/test_policy_compliance.py` success and error/edge-path coverage.

## 6. Risk assessment tool component

- [x] 6.1 Implement `assess_risk` in `tools/risk_assessment.py` using vendor compliance and contract status signals.
- [x] 6.2 Return structured `compliance_flag`, `contract_status`, and `risk_level` outputs.
- [x] 6.3 Add structured error output for unknown vendor IDs.
- [x] 6.4 Add `tests/test_risk_assessment.py` success and error/edge-path coverage.

## 7. Agent wiring and decision orchestration

- [x] 7.1 Construct the Pydantic AI agent in `agent.py` with `output_type=ProcurementRecommendation`.
- [x] 7.2 Wire all four tools into a deterministic evaluation pipeline.
- [x] 7.3 Implement precedence logic `escalate > deny > approve` for conflicting findings.
- [x] 7.4 Build rationale composition from tool findings with explicit policy/tool references.
- [x] 7.5 Implement fallback so unresolved tool/data failures return schema-valid `escalate` recommendations.

## 8. Integration tests and quality gates

- [x] 8.1 Add end-to-end tests for representative approve, deny, and escalate requests.
- [x] 8.2 Add integration tests for ambiguous and near-threshold cases with explicit assertions.
- [x] 8.3 Run `pytest tests/ -v --tb=short --junitxml=docs/test-results.xml` and fix failures.
- [x] 8.4 Commit `docs/test-results.xml` with code changes for RAPID ITC.003 compliance.

## 9. OpenSpec verification and handoff

- [x] 9.1 Run `openspec validate add-procurement-intelligence-agent` and resolve all validation issues.
- [x] 9.2 Mark completed checkboxes in this file as tasks finish in Sessions 2 and 3.
- [x] 9.3 Prepare implementation handoff summary and proceed with `/opsx:apply`.
