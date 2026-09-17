"""Release gates are evaluated against unrounded aggregate values."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ReleasePolicy:
    thresholds: dict

    def evaluate(self, before, after):
        thresholds = self.thresholds
        gates = []
        for metric, threshold in (("quality", "min_quality"), ("citation_rate", "min_citation_rate"),
                                  ("refusal_rate", "min_refusal_rate"), ("injection_rate", "min_injection_rate")):
            gates.append({"gate": metric, "actual": after[metric], "operator": ">=", "threshold": thresholds[threshold], "passed": after[metric] >= thresholds[threshold]})
        for metric, threshold in (("p95_latency_ms", "max_p95_latency_ms"), ("mean_cost_usd", "max_mean_cost_usd")):
            gates.append({"gate": metric, "actual": after[metric], "operator": "<=", "threshold": thresholds[threshold], "passed": after[metric] <= thresholds[threshold]})
        regression = before["quality"] - after["quality"]
        gates.append({"gate": "quality_regression", "actual": regression, "operator": "<=", "threshold": thresholds["max_quality_regression"], "passed": regression <= thresholds["max_quality_regression"]})
        return gates
