# Domain and AI contracts — AI Evaluation Release Gate

## Inputs

| Field | Behavior |
|---|---|
| `cases` | 2–200 cases locally; live transport applies its tighter provider budget. Each suite needs answerable, refusal and canary-challenge coverage. |
| `thresholds` | Explicit minimum quality/citation/refusal/injection rates and maximum regression, p95 latency and mean cost. |
| `illustrative_prices` | Nonnegative input/output USD rates per million tokens; illustrative inputs, not vendor quotes. |
| `experiment` | suite_version, baseline_prompt_version, candidate_prompt_version; seed 0–2³²−1; bootstrap_samples 100–2000 (default 400). |

## Evidence and failure semantics

Invented citations, incorrect numeric claims, missing refusal language, unauthorized actions, invalid gold labels, malformed cases, unknown policy keys and invalid experiment options are rejected or exposed by deterministic checks. Invalid input raises a controlled validation error. Optional provider errors remain errors; the runtime does not claim that a failed model call succeeded. The raw report is the source for UI, JSON export and saved execution comparison.

## Interpretation boundaries

- Exact evidence phrase matching can reject valid paraphrases and can miss unsupported additional statements. It is a transparent regression rubric, not a calibrated factuality oracle.
- Prompt version labels are declared metadata, not proof that different prompts were executed. Snapshot hashes bind actual response evidence, and live output has a separate evaluated digest.
- Bootstrap/Wilson intervals describe this finite synthetic suite. They do not establish production failure rates, adversarial robustness or regulatory approval.
- Offline timings/token counts are supplied snapshots. Live latency is measured, while token counts and cost are estimated. A pass advances a candidate to broader validation; it does not deploy it.

## Dataset origin

Committed examples are original synthetic data. Provider output snapshots in the examples are illustrative fixtures unless an individual execution explicitly records live mode. Synthetic examples demonstrate mechanisms; they are not measured employer, customer or production outcomes.
