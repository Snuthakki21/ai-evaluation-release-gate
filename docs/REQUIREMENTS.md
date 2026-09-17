# Requirements and verification map — AI Evaluation Release Gate

| Requirement | Implementation | Verification |
|---|---|
| R-01: Evaluation architecture | Evidence-grounded grading, refusal checks, citation validity/completeness, action allowlists and injection canaries. | Domain suites listed below; inspect current CI evidence. |
| R-02: Experiment reproducibility | Versioned suite and prompt labels; SHA-256 identities bind rubric data and response snapshots separately. Live evaluated rows have their own digest. | Domain suites listed below; inspect current CI evidence. |
| R-03: Paired analysis | Baseline and candidate share the same cases. Seeded resampling estimates descriptive uncertainty in the paired mean difference. | Domain suites listed below; inspect current CI evidence. |
| R-04: Failure diagnosis | Cohorts preserve regressions that an overall average can obscure; failed case text remains inspectable. | Domain suites listed below; inspect current CI evidence. |
| R-05: Release policy | Absolute quality, citation, refusal and injection gates plus baseline-regression, p95 latency and mean-cost budgets. | Domain suites listed below; inspect current CI evidence. |
| R-06: Bounded inference | Optional structured candidate generation with a JSON schema, provider budgets and validation; no autonomous release action. | Domain suites listed below; inspect current CI evidence. |

## Executable suites

- `tests/test_ai_release_gate.py`
- `tests/test_product_experiments.py`
- `tests/test_operations_independent.py`

## Acceptance checks

- Default and alternate scenarios execute through the public adapter and ProductApplication.
- Invalid inputs are rejected before optional provider execution.
- New domain results are rendered in the product interface and exported completely.
- Saved scenario/run workflows use the common platform and preserve input revisions.
- Current CI tests, static build and browser execution succeed for this repository.
- A separate automated reviewer examines expanded source and records findings with validation evidence.
