"""Evaluate one versioned candidate and return a complete release evidence package."""
from app.domain.validation import validate_suite
from app.domain.grading import EvidenceGrader, AggregateStatistics
from app.domain.policy import ReleasePolicy
from app.domain.experiments import ReleaseExperiment
from app.ai.candidate import CandidateGenerator

class ProductApplication:
    def run(self, payload, context=None):
        cases, thresholds, rates = validate_suite(payload)
        experiment = ReleaseExperiment.from_payload(payload, cases)
        live_calls = CandidateGenerator().generate(cases, context)
        grader = EvidenceGrader()
        baseline = [grader.grade(case, case["baseline"], rates) for case in cases]
        candidate = [grader.grade(case, case["candidate"], rates) for case in cases]
        before, after = AggregateStatistics.aggregate(baseline), AggregateStatistics.aggregate(candidate)
        gates = ReleasePolicy(thresholds).evaluate(before, after)
        passed = all(g["passed"] for g in gates)
        failures = [g["gate"] for g in gates if not g["passed"]]
        report = {
            "summary": ("Candidate passes this synthetic release suite; advance to broader validation." if passed else "Hold this candidate: release gates failed for " + ", ".join(failures) + "."),
            "metrics": [{"label": "Candidate rubric quality", "value": round(after["quality"] * 100, 2), "unit": "%"},
                        {"label": "Passed release gates", "value": sum(g["passed"] for g in gates), "unit": f"of {len(gates)}"},
                        {"label": "Candidate p95 latency", "value": after["p95_latency_ms"], "unit": "ms"},
                        {"label": "Illustrative mean cost", "value": round(after["mean_cost_usd"], 6), "unit": "USD/case"}],
            "evidence": [f"Graded {len(cases)} original synthetic cases from response text, citations, refusal flags and attempted actions.",
                         f"Baseline quality {before['quality']:.1%}; candidate quality {after['quality']:.1%} on this suite only.",
                         (f"{live_calls} candidate responses came from a real model; live latency was measured, token cost was estimated." if live_calls else "Both response sets are original synthetic snapshots; latency and tokens are declared fixture inputs, not measured model performance."),
                         "Evidence matching is deliberately exact and can miss unsupported extra claims; review transcripts and use a calibrated semantic grader before production.",
                         "Prices are illustrative and not current vendor quotes."],
            "next_actions": (["Add independently authored holdout cases and calibrate graders against human review.", "Run repeated live trials before deciding on a production release."] if passed else ["Inspect failed gates and per-case transcripts before rerunning.", "Fix the candidate or explicitly review the release policy; do not hide failing cases."]),
            "details": {"release_decision": "advance_to_validation" if passed else "hold", "gates": gates,
                        "baseline_aggregate": before, "candidate_aggregate": after, "baseline_cases": baseline,
                        "candidate_cases": candidate, "prices": rates, "live_candidate_calls": live_calls,
                        "rubric": "Mean of expected-claim coverage, citation completeness/validity, refusal correctness and forbidden-content/action checks. Injection metric is a fixture canary check, not general prompt-injection immunity."},
        }
        report["details"].update(experiment.analyze(cases, baseline, candidate))
        return report
