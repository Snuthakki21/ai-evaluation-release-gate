"""Reproducible suite identity, paired uncertainty and cohort error analysis."""
from dataclasses import dataclass
from hashlib import sha256
import json
import math
import random


def fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def wilson(successes, count, z=1.96):
    """Two-sided Wilson score interval for a binary pass frequency."""
    if count == 0:
        return [0.0, 1.0]
    p = successes / count
    denominator = 1 + z*z/count
    center = (p + z*z/(2*count)) / denominator
    half = z*math.sqrt(p*(1-p)/count + z*z/(4*count*count))/denominator
    return [max(0, center-half), min(1, center+half)]


@dataclass(frozen=True)
class ExperimentIdentity:
    suite_version: str
    baseline_prompt_version: str
    candidate_prompt_version: str
    seed: int
    bootstrap_samples: int

    @classmethod
    def from_payload(cls, payload):
        config = payload.get("experiment", {})
        defaults = {"suite_version": "operations-policy-v1", "baseline_prompt_version": "evidence-v1",
                    "candidate_prompt_version": "evidence-v2", "seed": 417, "bootstrap_samples": 400}
        if not isinstance(config, dict) or set(config)-set(defaults):
            raise ValueError("Unknown experiment identity or bootstrap option.")
        defaults.update(config)
        for key in ("suite_version", "baseline_prompt_version", "candidate_prompt_version"):
            if not isinstance(defaults[key], str) or not 1 <= len(defaults[key]) <= 120:
                raise ValueError("Suite and prompt versions must be 1–120 character identifiers.")
        if type(defaults["seed"]) is not int or not 0 <= defaults["seed"] <= 2**32-1:
            raise ValueError("Experiment seed must be an unsigned 32-bit integer.")
        if type(defaults["bootstrap_samples"]) is not int or not 100 <= defaults["bootstrap_samples"] <= 2000:
            raise ValueError("Bootstrap samples must be an integer from 100 to 2000.")
        return cls(**defaults)


@dataclass(frozen=True)
class ReleaseExperiment:
    identity: ExperimentIdentity
    suite_hash: str
    prompt_hashes: dict

    @classmethod
    def from_payload(cls, payload, cases):
        identity = ExperimentIdentity.from_payload(payload)
        rubric = [{key: value for key, value in case.items() if key not in {"baseline", "candidate"}} for case in cases]
        return cls(identity, fingerprint(rubric), {
            "baseline": fingerprint([identity.baseline_prompt_version, [c["baseline"] for c in cases]]),
            "candidate": fingerprint([identity.candidate_prompt_version, [c["candidate"] for c in cases]])})

    def analyze(self, cases, baseline, candidate):
        rng = random.Random(self.identity.seed)
        deltas = [b["quality"]-a["quality"] for a, b in zip(baseline, candidate)]
        draws = sorted(sum(rng.choice(deltas) for _ in deltas)/len(deltas)
                       for _ in range(self.identity.bootstrap_samples))
        interval = [draws[int(.025*(len(draws)-1))], draws[int(.975*(len(draws)-1))]]
        pass_count = sum(row["quality"] == 1 for row in candidate)
        cohorts = []
        definitions = {
            "answerable": lambda c: not c["must_refuse"],
            "refusal": lambda c: c["must_refuse"],
            "injection canary": lambda c: bool(c["forbidden_terms"]),
        }
        for name, predicate in definitions.items():
            indices = [i for i, case in enumerate(cases) if predicate(case)]
            cohorts.append({"cohort": name, "cases": len(indices),
                            "baseline_quality": round(sum(baseline[i]["quality"] for i in indices)/len(indices), 4),
                            "candidate_quality": round(sum(candidate[i]["quality"] for i in indices)/len(indices), 4),
                            "regressions": [cases[i]["id"] for i in indices if deltas[i] < 0],
                            "failed_case_ids": [cases[i]["id"] for i in indices if candidate[i]["quality"] < 1]})
        errors = []
        for before, after in zip(baseline, candidate):
            reasons = [field for field in ("citation_pass", "refusal_pass", "injection_pass") if not after[field]]
            if after["coverage"] < 1:
                reasons.append("claim_coverage")
            if reasons or after["quality"] < before["quality"]:
                errors.append({"case": after["id"], "quality_delta": round(after["quality"]-before["quality"],4),
                               "failure_dimensions": reasons, "candidate_answer": after["answer"]})
        total_cost = sum(row["cost_usd"] for row in candidate)
        total_latency = sum(row["latency_ms"] for row in candidate)
        return {
            "experiment_identity": {"suite_version": self.identity.suite_version, "suite_sha256": self.suite_hash,
                "baseline_prompt_version": self.identity.baseline_prompt_version,
                "candidate_prompt_version": self.identity.candidate_prompt_version,
                "snapshot_sha256": self.prompt_hashes,
                "evaluated_candidate_sha256": fingerprint(candidate),
                "identity_note": "Prompt version labels are declared metadata; hashes bind the actual suite and response snapshots."},
            "uncertainty": {"paired_quality_delta": sum(deltas)/len(deltas),
                "bootstrap_95_interval": interval, "full_case_pass_95_wilson_interval": wilson(pass_count, len(cases)),
                "seed": self.identity.seed, "bootstrap_samples": self.identity.bootstrap_samples,
                "interpretation": "Descriptive resampling of this finite synthetic suite; not evidence of production generalization or independent human judgments."},
            "cohort_analysis": cohorts, "error_analysis": errors,
            "operating_envelope": {"candidate_total_cost_usd": round(total_cost, 8),
                "candidate_serial_latency_ms": total_latency, "cost_per_fully_passing_case_usd": round(total_cost/pass_count,8) if pass_count else None,
                "fully_passing_cases": pass_count, "cases": len(cases), "token_cost_is_estimated": True}}
