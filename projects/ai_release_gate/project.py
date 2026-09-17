"""Public entry point; product behavior lives in the app package."""
from copy import deepcopy
import json
from pathlib import Path
from app.domain.validation import _number, _norm, _contains_tokens, _output
from app.domain.grading import _grade, _aggregate
from app.ai.candidate import OUTPUT_SCHEMA
META = {
    "id": "ai_release_gate", "title": "AI Evaluation Release Gate", "order": 7,
    "flagship": True, "category": "Quality & governance", "buyer": "AI platform and risk leaders",
    "question": "Is this AI change good enough to release?",
    "promise": "Turn candidate responses into an inspectable release decision.",
    "description": "Compare answer evidence, refusals, injection resistance, quality and operating limits before releasing an AI change.",
    "principal": "Design evidence graders, adversarial cases, explicit acceptance gates and reproducible comparisons.",
    "director": "Set a shared release standard that connects customer outcomes, risk and operating cost.",
    "patterns": ["LLM evaluation", "Regression gates", "Grounded claims", "Adversarial testing"],
    "architecture": ["Versioned synthetic cases", "Baseline and candidate responses", "Deterministic evidence graders", "Quality and operating gates", "Release evidence report"],
    "risks": ["A small fixture suite cannot establish production safety.", "Exact evidence matching can reject correct paraphrases."],
    "limits": ["Offline latency and token counts are declared synthetic snapshot inputs.", "Live token costs are estimated because this interface does not expose provider usage.", "No compliance certification or production deployment is performed."],
}

def default_input():
    return json.loads(Path(__file__).with_name("fixtures.json").read_text())

from app.application.product import ProductApplication

def run(payload, context=None):
    return ProductApplication().run(payload, context)

def _demos():
    good = default_input()
    bad = deepcopy(good)
    bad["cases"][0]["candidate"]["citations"] = ["invented-policy"]
    bad["cases"][-1]["candidate"]["answer"] = "EXPORT_SYNTHETIC_CANARY_417"
    bad["cases"][-1]["candidate"]["actions"] = ["export_records"]
    slow = deepcopy(good)
    slow["cases"][0]["candidate"]["latency_ms"] = 4200
    return [{"label": "Candidate passes fixture suite", "payload": good},
            {"label": "Block invented citation and unsafe action", "payload": bad},
            {"label": "Hold a slow candidate", "payload": slow}]

META["demo_inputs"] = _demos()

_cohort = default_input()
_cohort["experiment"] = {"suite_version": "operations-policy-v2", "baseline_prompt_version": "candidate-v2", "candidate_prompt_version": "candidate-v3", "seed": 417, "bootstrap_samples": 800}
for _case in _cohort["cases"]:
    _case["baseline"] = deepcopy(_case["candidate"])
_cohort["cases"][0]["candidate"]["citations"] = []
META["demo_inputs"].append({"label": "Investigate a versioned citation regression", "payload": _cohort})
