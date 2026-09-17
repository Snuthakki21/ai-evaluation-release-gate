# Independent automated Staff Engineer review — expanded application

Review date: 2026-09-17. A separate automated reviewer, independent of the product author, examined the current expanded source. This is an automated engineering review, not an external human audit or production certification.

## Scope and method

Read the current product diff, product requirements, actual domain/application/AI services, compatibility adapter, product UI template and author tests. Independently designed adverse-input tests in `tests/test_product_review.py` and rendering tests in `tests/product-review-ui.test.mjs`. The product author corrected implementation findings; the reviewer retested those changes.

This domain review excludes an independent audit of shared persistence/HTTP code, distribution packaging, hosted CI and live-browser visual quality. The whole existing Python suite was executed for regression evidence; that execution does not expand the source-review scope. Live provider accuracy and real financial outcomes were not measured.

## Verdict

**Pass for the documented product scope after independent verification. No unresolved implementation finding was reproduced in this review.** The verdict applies to the attached source snapshot and executed checks. It does not assert a defect-free or production-certified system.

## Requirements and architecture assessment

R-01 through R-06: exact evidence/refusal/citation/action checks; reproducible identity; paired uncertainty; cohort failures; full-precision release gates; validation before bounded optional inference.

EvidenceGrader and AggregateStatistics calculate raw decision operands; ReleasePolicy owns gate comparisons. Immutable experiment identity records bind suite and response snapshots, while ReleaseExperiment owns paired bootstrap intervals, cohort diagnosis and operating summaries. ProductApplication coordinates these responsibilities and the optional candidate-generation boundary. These are substantive policies and analyses, not wrappers around a duplicated monolithic engine.

New results are calculated by the domain services, rendered in the product-specific template and included in full downloadable reports. Independent UI checks confirm all published scenarios render without undefined or NaN values, preserve result evidence and escape hostile labels. Common workspace actions are assessed separately.

## Findings and resolution

### RG-1 — P2: Premature per-case rounding could advance a failing release threshold.

Reproduction: A seven-claim case with six covered claims yielded a true suite quality of 0.5580357142857142 but a rounded aggregate of 0.5580375; a threshold between those values passed. Cost rounding similarly obscured a 1.4e-8 cost against a 1.2e-8 ceiling.

Resolution and retest: EvidenceGrader now preserves full-precision coverage, quality and cost. ReleasePolicy exposes exact decision operands in the JSON report. Independent quality and subcent-cost regressions both pass.

Status: closed by an author implementation change and independent regression verification.

## Executed verification

- Full Python suite: 137 tests, zero failures, 0 explicit skips.
- Independent domain regressions: 6 passed as part of that run.
- Static build: the standalone product and all declared examples built successfully.
- Frontend and independent product UI tests: 34 total, 28 passed, 6 explicit absent-project skips, zero failures. Three checks specifically exercise the expanded UI.

```sh
python3 -m unittest discover -s tests
python3 -m portfolio build --output dist
node --test --test-timeout=20000 tests/frontend.test.mjs tests/product-review-ui.test.mjs
```

## Source snapshot

[Machine-readable SHA-256 snapshot](STAFF_REVIEW_V2_SOURCE.json) identifies every reviewed domain module, compatibility adapter, template, independent test and current requirement document. Future material edits require renewed review of changed behavior.

| File | SHA-256 |
|---|---|
| `app/ai/__init__.py` | `3b3a14d073c138b40d988b4b8190df8e8a9260df4a601bc5f4a01bc3e5eed029` |
| `app/ai/candidate.py` | `9dd74152992940d0145c2c9b34a2548ea5a0078f9e79ba23b12488c0a4fb4cf3` |
| `app/application/__init__.py` | `4ca85bbc1f8ce81b55960e4222fee1429279e38bef72bf3070d2b1ee65bf17d7` |
| `app/application/product.py` | `9d53ac589a656b63017cdf07e773d754bd40d49f3aa2b72f50a7172ef064651e` |
| `app/domain/__init__.py` | `2a0b1d756023f313f1d4280a19ba351434ebdbaafc2a3a6e3cde02992dcfe982` |
| `app/domain/experiments.py` | `d023f8d031840aac70b98a613b452f0514525b866db3a642a2ad1eb25be68e95` |
| `app/domain/grading.py` | `92e6393d8f60bdf931005eed7d40e02c414b86064017dfaf82aaf6aab29cce33` |
| `app/domain/policy.py` | `9295143b31e5f7a569ebb281f8497d5fda6a496adbccd35b44b876ddaecebe18` |
| `app/domain/validation.py` | `81d26fbb03f818bb36a638ec95eed48f7764744f4fe1b01730bf522d6ab42688` |
| `docs/PRODUCT.md` | `e2638c650cf3a9cad3669a8da213e5eedd2c7ec7f038d9041570f2808d4cd927` |
| `docs/REQUIREMENTS.md` | `4cf0c55de37fff2f43de696f2332d1dd27023174529d7c371dd845223219bb8a` |
| `projects/ai_release_gate/project.py` | `078681d50a17ba914f5c4e5f1425990a59c5e1941e4508ac9dc1704f59c958b0` |
| `tests/product-review-ui.test.mjs` | `51510cd0531b993f4396e3363458ced2f3810f837fe794d54992b23022a11d6c` |
| `tests/test_product_review.py` | `7fc5ed48853e5e642feb7c13b29c1409fc16b8e24519645eb3e8b2ecdd6a62f8` |
| `web/templates/ai_release_gate.js` | `bba0771c67f1b7551de285c52c4c9692e66e851a0611e0b5836d0db619a4b4ac` |
