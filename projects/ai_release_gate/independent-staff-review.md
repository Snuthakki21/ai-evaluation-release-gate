# Independent Staff Engineer review

Reviewed on 2026-09-17.

Reviewer: independent automated agent operating in a Staff Engineer review role. The reviewer did not author or change this project's implementation. Author fixes were requested with concrete reproductions and independently rechecked. This is not a human sign-off or a claim that all possible failures were tested.

Scope: project requirements in CONTRIBUTING.md, this project's README, project.py, original fixture data, its author unit suite and the independent regressions. Shared provider/network handling, browser UI, deployment configuration and real production data are outside this review.

## Findings and resolution

**REL-01 · P2 · Resolved — Numeric substrings could satisfy a different factual claim.** With the retained-log case's expected claim set to `30 days`, candidate text `Synthetic test logs are retained for 130 days.` originally received coverage 1.0, a passing citation result and `advance_to_validation`. The source correctly stated 30 days. `_grade` used raw substring containment after normalization, so a wrong numeric token could satisfy the rubric.

The author added whole-normalized-token matching to expected-claim coverage, cited support and gold/source validation. Independent tests now require the changed answer to produce zero coverage, failed citation completeness and `hold`; a source that only contains 130 days can no longer validate the gold claim 30 days.

## Additional boundary checks

A malformed final case and a missing injection-challenge suite both reject with zero calls to a controlled live-context counter. This verifies the parent's requested prevalidation boundary without making paid calls. Live candidate prompts remain separated from expected claims and gold labels. Existing tests retain source-reference checks, refusal-language checks, attempted-action rejection, latency boundaries and cost arithmetic.

## Verdict and remaining limits

**PASS for the reviewed synthetic evaluation contract at the source hash below.** The reproduced token-boundary defect is fixed. Exact expected-claim matching still cannot detect every unsupported additional assertion or validate all paraphrases, as documented. Snapshot latency/tokens are declared inputs; test doubles do not establish live-provider factuality or prompt-injection resistance. A passing toy suite is an advance-to-validation decision, not production release authorization.

## Reproducible verification

```sh
python -m unittest discover -s tests -p 'test_ai_release_gate.py' -v
python -m unittest discover -s tests -p 'test_operations_independent.py' -v
```

The final local run passed 15 author tests for this project and 4 independent project-specific tests. The complete independent file passed all 18 tests across four review scopes. When copied to a single-project repository, tests for absent projects are explicitly skipped, not counted as that project's validation.

Final reviewed `project.py` SHA-256: `41dc5447ea34d13b5edffb7c286168659d8358470f261b9c2ca7458e090c307a`.

Independent regression file SHA-256: `28392166c7fc198d671c9cb78fc143810e23600e76d0b3b0cbf9e94e911fa7ca`.

The verdict applies to the identified source. Any later implementation change requires rechecking the affected behavior. No live paid call, production write, external account action or destructive security payload was performed during this review.
