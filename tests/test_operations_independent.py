"""Independent Staff Engineer regressions; author modules are not modified here.

Classes skip only when their project is absent from a standalone export.
"""

from copy import deepcopy

from decimal import Decimal

import importlib

import unittest

def load_project(project_id):
    try:
        return importlib.import_module(f"projects.{project_id}.project")
    except ModuleNotFoundError as exc:
        if exc.name in {f"projects.{project_id}", f"projects.{project_id}.project"}:
            raise unittest.SkipTest("This standalone repository does not contain that project") from exc
        raise

class IndependentReleaseGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = load_project("ai_release_gate")

    def test_numeric_suffix_is_not_an_exact_expected_claim(self):
        data = self.project.default_input()
        data["cases"][1]["expected_claims"] = ["30 days"]
        data["cases"][1]["candidate"]["answer"] = "Synthetic test logs are retained for 130 days."
        result = self.project.run(data)["details"]
        self.assertEqual(result["release_decision"], "hold")
        self.assertEqual(result["candidate_cases"][1]["coverage"], 0)
        self.assertFalse(result["candidate_cases"][1]["citation_pass"])

    def test_gold_claim_must_match_whole_source_tokens(self):
        data = self.project.default_input()
        data["cases"][1]["expected_claims"] = ["30 days"]
        data["cases"][1]["documents"][0]["text"] = "Synthetic logs are retained for 130 days."
        with self.assertRaises(ValueError):
            self.project.run(data)

    def test_invalid_final_case_prevents_every_provider_call(self):
        class CounterContext:
            mode = "live"
            count = 0
            def generate_json(self, **kwargs):
                self.count += 1
                return {"answer": "I cannot answer.", "citations": [], "refused": True, "actions": []}
        data = self.project.default_input()
        data["cases"][-1]["question"] = None
        context = CounterContext()
        with self.assertRaises(ValueError):
            self.project.run(data, context)
        self.assertEqual(context.count, 0)

    def test_suite_coverage_error_prevents_every_provider_call(self):
        class CounterContext:
            mode = "live"
            count = 0
            def generate_json(self, **kwargs):
                self.count += 1
                return {"answer": "I cannot answer.", "citations": [], "refused": True, "actions": []}
        data = self.project.default_input()
        for case in data["cases"]:
            case["forbidden_terms"] = []
        context = CounterContext()
        with self.assertRaises(ValueError):
            self.project.run(data, context)
        self.assertEqual(context.count, 0)

if __name__ == "__main__":
    unittest.main()
