# Engineering review: AI Evaluation Release Gate

This records the actual author-side checks and plugin-guided contributions. It is a self-review, not the independent Staff Engineer audit requested for delivery. The independent review is a separate artifact supplied by a non-authoring reviewer.

## Brooks-Lint Architecture Audit

**Scope:** This project module, original fixture, and its unit tests. Shared runtime internals and other applications are outside this author-side audit. No project-specific Brooks configuration was present. **Health Score: 100/100 after repairs** (structural assessment only; this is not a security, production-readiness or test score).

### Module Dependency Graph

```mermaid
graph TD
    Runtime[Shared CLI or API caller] --> Project[Project run boundary]
    Tests[Project unittest suite] --> Project
    Project --> Fixtures[Original local JSON fixtures]
    Project --> Standard[Python standard library]
    Project --> Context[Optional context seam or no-model policy]
    classDef clean fill:#51cf66,stroke:#2b8a3e,color:#fff
    class Runtime,Tests,Project,Fixtures,Standard,Context clean
```

### Findings

No unresolved structural finding in this bounded scope. The module imports only `json, pathlib, re, time, math, copy`. There is no project-to-project import or circular dependency. The program has one domain purpose and one public run boundary; its DTO-style inputs are an intentional boundary contract. An in-memory SQLite dependency in analytics is a local adapter decision, not an external service dependency. Optional context.generate_json candidate interface.

The review scanned dependency disorder, domain-model distortion, duplicated decisions, accidental complexity, change propagation and cognitive load. Guard clauses and linear orchestration were retained where they make trust boundaries visible. No factories, provider hierarchy or agent framework were added. The testability seam is the explicit context parameter; local deterministic behavior is tested without network access. Team structure beyond this personal portfolio is unknown, so no Conway's Law claim is made.

Resolved correctness observations:

- Refusal evaluation initially trusted only the Boolean flag. Added explicit refusal-language validation and a regression test, so a claimed refusal with “completed” language fails.
- Normalized gold-label validation now rejects punctuation-only claims rather than treating an empty normalized string as evidence.

The reasoning follows *Code Complete* defensive construction, *The Pragmatic Programmer* orthogonality, and *Working Effectively with Legacy Code* seams where those principles match the concrete observations. Similar small validators across independently deployable bounded projects are not treated as an automatic DRY violation.

## Ponytail ultra contribution

The implementation stops at the standard library and a small explicit workflow. It reuses the shared provider seam instead of creating another client. Known simplification ceilings are marked with `ponytail:` comments in code. User-requested security validation, tests and thorough documentation are retained. No speculative distributed service, database deployment or autonomous orchestration was added.

## Claude Octopus coverage audit

Detected convention: Python standard-library `unittest`, `tests/test_<project_id>.py`, xUnit classes and built-in assertions. This audit prioritized fewer than 30 high-risk behavior groups and generated fewer than 20 test methods for this project. The inventory below maps asserted outcomes and failure boundaries; it is not a claim that one method equals one branch.

| # | Behavior group | Type | Test method | Assessment |
|---|---|---|---|---|
| 1 | reference candidate passes all gates | conditional/outcome | `test_reference_candidate_passes_all_gates` | Behavior asserted |
| 2 | missing claim holds release | conditional/outcome | `test_missing_claim_holds_release` | Behavior asserted |
| 3 | invalid source is not accepted | error/guard | `test_invalid_source_is_not_accepted` | Behavior asserted |
| 4 | canary and action are detected | conditional/outcome | `test_canary_and_action_are_detected` | Behavior asserted |
| 5 | refusal flag needs actual refusal language | conditional/outcome | `test_refusal_flag_needs_actual_refusal_language` | Behavior asserted |
| 6 | latency limit holds release | conditional/outcome | `test_latency_limit_holds_release` | Behavior asserted |
| 7 | cost gate is computed from tokens | conditional/outcome | `test_cost_gate_is_computed_from_tokens` | Behavior asserted |
| 8 | threshold boundary and policy override | error/guard | `test_threshold_boundary_and_policy_override` | Behavior asserted |
| 9 | bad suite is rejected | error/guard | `test_bad_suite_is_rejected` | Behavior asserted |
| 10 | live candidate has no gold labels and is checked | integration | `test_live_candidate_has_no_gold_labels_and_is_checked` | Behavior asserted |
| 11 | local none is not claimed as live | integration | `test_local_none_is_not_claimed_as_live` | Behavior asserted |
| 12 | input is not mutated | conditional/outcome | `test_input_is_not_mutated` | Behavior asserted |
| 13 | schema boundaries reject invalid outputs and cases | error/guard | `test_schema_boundaries_reject_invalid_outputs_and_cases` | Behavior asserted |
| 14 | live none fallback preserves fixture disclosure | integration | `test_live_none_fallback_preserves_fixture_disclosure` | Behavior asserted |
| 15 | invalid later case makes zero provider calls | integration/error | `test_invalid_later_case_prevents_all_live_calls` | Behavior asserted |

```text
SELECTED BEHAVIORS: 15/15 mapped to assertions
UNIT TEST METHODS: 15 passing
MEASURED STATEMENT + BRANCH COVERAGE, FINAL REVIEW RUN: 100.00%
```

Coverage was run with `coverage run --branch --source=projects.ai_release_gate -m unittest tests.test_ai_release_gate` as part of the four-project author test run. Across these four modules, 64 author tests and 18 independent review tests passed (82 total). Liquidity's sole uncovered line is the internal arithmetic-conservation exception; normal and stressed conservation outcomes are checked across every bucket. Analytics retains three redundant guard error branches already intercepted by earlier vocabulary/scope validation; these are reported as uncovered, not excluded from measurement. No coverage percentage implies that all economic assumptions or live model behavior have been validated.

## Development Skills staff-review status

The staff-review skill was read. Its required `development-skills:staff-reviewer` dispatch target was not present as a callable local agent definition in the installed package. That specific dispatch was not claimed. A factual author-side trace checked the requested project contract, run behavior, invalid inputs and current unit results. A non-authoring operations agent completed the independent automated review and rechecked the author corrections. See [independent-staff-review.md](independent-staff-review.md) for its source hash, reproductions and bounded PASS verdict.

## Accepted scope limits

- Exact phrase coverage cannot establish that every additional sentence is grounded. This is prominently disclosed; a calibrated semantic grader remains production work.
- Snapshot token/latency fields are fixture inputs. Live generation measures wall time but estimates token usage.

These are published application limits, not silently waived production requirements. See the README for input/output, operations, test procedure, alternatives and production work.

## Final cross-review follow-through

Independent review prompted whole-token claim/source matching and complete case validation before provider calls. The corrected code rejects 130-day claims when the gold value is 30 days and makes zero calls when a later case is invalid.

Final measured coverage includes the author suite and `tests/test_operations_independent.py`; it does not imply a real model benchmark. Reviewed implementation SHA-256: `41dc5447ea34d13b5edffb7c286168659d8358470f261b9c2ca7458e090c307a`.
