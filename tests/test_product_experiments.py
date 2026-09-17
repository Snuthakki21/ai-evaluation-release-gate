"""Domain contracts for versioned release experiments and uncertainty."""
from copy import deepcopy
import unittest
from app.application.product import ProductApplication
from app.domain.experiments import ExperimentIdentity, ReleaseExperiment, wilson
from app.domain.policy import ReleasePolicy
from app.domain.validation import validate_suite
from projects.ai_release_gate.project import default_input, run

class ReleaseExperimentTests(unittest.TestCase):
    def test_application_preserves_public_entry_point(self):
        self.assertEqual(ProductApplication().run(default_input()), run(default_input()))

    def test_seeded_bootstrap_and_identity_are_reproducible(self):
        first=run(default_input())["details"];second=run(default_input())["details"]
        self.assertEqual(first["uncertainty"],second["uncertainty"])
        self.assertEqual(first["experiment_identity"],second["experiment_identity"])
        low,high=first["uncertainty"]["bootstrap_95_interval"]
        self.assertLessEqual(low,first["uncertainty"]["paired_quality_delta"])
        self.assertGreaterEqual(high,first["uncertainty"]["paired_quality_delta"])

    def test_version_labels_do_not_change_quality(self):
        data=default_input();original=run(data)["details"]
        data["experiment"]={"candidate_prompt_version":"new-prompt-v9"}
        changed=run(data)["details"]
        self.assertEqual(original["candidate_aggregate"],changed["candidate_aggregate"])
        self.assertNotEqual(original["experiment_identity"]["snapshot_sha256"],changed["experiment_identity"]["snapshot_sha256"])
        self.assertEqual(original["experiment_identity"]["suite_sha256"],changed["experiment_identity"]["suite_sha256"])

    def test_case_content_is_bound_separately_from_response_snapshot(self):
        data=default_input();before=run(data)["details"]["experiment_identity"]
        data["cases"][0]["candidate"]["answer"]="No answer."
        after=run(data)["details"]["experiment_identity"]
        self.assertEqual(before["suite_sha256"],after["suite_sha256"])
        self.assertNotEqual(before["snapshot_sha256"]["candidate"],after["snapshot_sha256"]["candidate"])
        data["cases"][0]["question"]+=" Please."
        self.assertNotEqual(after["suite_sha256"],run(data)["details"]["experiment_identity"]["suite_sha256"])

    def test_error_cohorts_identify_regression(self):
        data=default_input();data["cases"][2]["candidate"]["citations"]=["invented"]
        result=run(data)["details"]
        self.assertEqual(result["error_analysis"][0]["case"],data["cases"][2]["id"])
        self.assertIn("citation_pass",result["error_analysis"][0]["failure_dimensions"])
        self.assertIn(data["cases"][2]["id"],result["cohort_analysis"][0]["regressions"])

    def test_same_baseline_candidate_has_zero_paired_interval(self):
        data=default_input()
        for case in data["cases"]:case["baseline"]=deepcopy(case["candidate"])
        self.assertEqual(run(data)["details"]["uncertainty"]["bootstrap_95_interval"],[0,0])

    def test_wilson_interval_does_not_claim_certainty_from_few_successes(self):
        self.assertLess(wilson(8,8)[0],.8)
        self.assertEqual(wilson(0,0),[0,1])
        self.assertLess(wilson(0,8)[1],.5)

    def test_operating_envelope_reconciles_case_evidence(self):
        details=run(default_input())["details"];envelope=details["operating_envelope"]
        self.assertAlmostEqual(envelope["candidate_total_cost_usd"],sum(c["cost_usd"] for c in details["candidate_cases"]))
        self.assertEqual(envelope["candidate_serial_latency_ms"],sum(c["latency_ms"] for c in details["candidate_cases"]))

    def test_invalid_experiment_is_rejected_before_any_live_call(self):
        class Context:
            mode="live"
            def generate_json(self,**kwargs):raise AssertionError("A provider call must not occur.")
        for config in [{"seed":True},{"seed":-1},{"seed":2**32},{"bootstrap_samples":99},{"bootstrap_samples":2001},{"bootstrap_samples":True},{"suite_version":""},{"candidate_prompt_version":4},{"other":1},[]]:
            with self.subTest(config=config),self.assertRaises(ValueError):
                data=default_input();data["experiment"]=config;run(data,Context())

    def test_fractional_grades_and_tiny_costs_retain_decision_precision(self):
        data=default_input();case=data['cases'][0]
        case['expected_claims']=[f'Claim number {i} is supported' for i in range(7)]
        case['documents'][0]['text']='. '.join(case['expected_claims'])
        case['candidate']['answer']='. '.join(case['expected_claims'][:6])
        data['illustrative_prices']={'input_per_million':.00001,'output_per_million':.00001}
        details=run(data)['details'];graded=details['candidate_cases'][0]
        self.assertEqual(graded['coverage'],6/7)
        self.assertEqual(graded['quality'],(6/7+2)/4)
        self.assertEqual(graded['cost_usd'],(450*.00001+55*.00001)/1_000_000)
        gate=next(g for g in details['gates'] if g['gate']=='quality')
        self.assertEqual(gate['actual'],details['candidate_aggregate']['quality'])

    def test_boundary_experiment_options(self):
        for samples in (100,2000):
            identity=ExperimentIdentity.from_payload({"experiment":{"bootstrap_samples":samples,"seed":0}})
            self.assertEqual(identity.bootstrap_samples,samples)

if __name__=="__main__":unittest.main()
