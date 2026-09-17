# Product runbook — AI Evaluation Release Gate

## Normal operation

1. Start the native app or open the static browser app. Confirm the scenario and execution mode.
2. Load an example or import a validated input. Save a scenario revision before changing assumptions.
3. Execute the domain workflow. Read the summary, failed controls and full evidence before recording a review.
4. Compare saved runs with the same question and scenario scope. Export input and report together for reproduction.
5. Use the native workspace backup/export controls before moving or deleting local storage. Browser-local storage must be exported before clearing browser data.

## Product-specific review

- **Review a candidate:** Load a case suite, set baseline and candidate prompt-version labels, inspect the expected claims and source documents, then grade both snapshots. The report holds the candidate whenever any configured gate fails.
- **Investigate a regression:** Use cohort analysis and error analysis to separate answerable cases, refusals and injection canaries. Inspect missing claims, unsupported claims, invalid citations, forbidden actions and the original candidate answer.
- **Assess statistical and operating uncertainty:** Read paired quality deltas, seeded bootstrap intervals and Wilson intervals alongside sample size. Compare total illustrative cost, serial evaluation time and cost per fully passing case before deciding whether to collect a larger holdout.
- **Evaluate a real candidate model:** Run the native service with a configured provider. Validation completes before the first model call. The candidate receives only the question and untrusted source documents, never expected answers or gold labels. Wall-clock latency is measured; tokens and cost remain estimates.

## Fault handling

| Symptom | Resolution |
|---|---|
| Input rejected | Match the bounded schema in DOMAIN_CONTRACTS; do not weaken validation to fit malformed data. |
| Unexpected calculation | Export the exact input and full report, then reproduce through the CLI and inspect the named domain service. |
| Optional provider failure | Check model/endpoint settings and schema; retain the failed result as a failure, not an approval. |
| Old UI/source | Rebuild the site and restart the native process after Python changes. |
| Workspace conflict | Reload the latest revision before applying changes; preserve conflicting edits in a separate scenario. |
| Browser storage missing | Check origin and browser profile. Static and native workspaces do not share a database. |

## Change and recovery procedure

Run domain and full application tests after a rule change. Regenerate example outputs, inspect affected decisions and request an independent review of changed boundaries. Keep source/version evidence with exported reports. Do not relabel historical validation as a review of later source.

## Deployment scope

Native service is a local single-operator workspace unless an authenticated deployment is explicitly implemented. Public Pages is a client-side application. No multi-user authorization, production SLA, compliance certification or real financial transaction execution is implied by a passing test suite.
