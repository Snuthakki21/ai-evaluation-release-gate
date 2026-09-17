import unittest
from copy import deepcopy
from projects.ai_release_gate.project import META, default_input, run

class ReleaseGateTests(unittest.TestCase):
    def test_reference_candidate_passes_all_gates(self):
        d=run(default_input())["details"]
        self.assertEqual(d["release_decision"],"advance_to_validation")
        self.assertTrue(all(g["passed"] for g in d["gates"]))
        self.assertGreater(d["candidate_aggregate"]["quality"],d["baseline_aggregate"]["quality"])

    def test_missing_claim_holds_release(self):
        p=default_input();p["cases"][0]["candidate"]["answer"]="No useful answer."
        r=run(p)["details"]
        self.assertEqual(r["release_decision"],"hold")
        self.assertEqual(r["candidate_cases"][0]["coverage"],0)

    def test_invalid_source_is_not_accepted(self):
        p=default_input();p["cases"][0]["candidate"]["citations"]=["invented"]
        r=run(p)["details"]
        self.assertEqual(r["candidate_cases"][0]["invalid_citations"],["invented"])
        self.assertEqual(r["release_decision"],"hold")

    def test_canary_and_action_are_detected(self):
        d=run(META["demo_inputs"][1]["payload"])["details"]
        self.assertFalse(d["candidate_cases"][-1]["injection_pass"])
        self.assertIn("export_records",d["candidate_cases"][-1]["forbidden_actions"])

    def test_refusal_flag_needs_actual_refusal_language(self):
        p=default_input();p["cases"][-1]["candidate"]["answer"]="Sure, completed."
        self.assertFalse(run(p)["details"]["candidate_cases"][-1]["refusal_pass"])

    def test_latency_limit_holds_release(self):
        d=run(META["demo_inputs"][2]["payload"])["details"]
        self.assertEqual(d["release_decision"],"hold")
        self.assertEqual(d["candidate_aggregate"]["p95_latency_ms"],4200)

    def test_cost_gate_is_computed_from_tokens(self):
        p=default_input();p["cases"][0]["candidate"]["output_tokens"]=100000
        r=run(p)["details"]
        self.assertEqual(r["release_decision"],"hold")
        self.assertGreater(r["candidate_cases"][0]["cost_usd"],0.4)

    def test_threshold_boundary_and_policy_override(self):
        p=default_input();p["thresholds"]={"max_p95_latency_ms":920}
        self.assertEqual(run(p)["details"]["release_decision"],"advance_to_validation")
        p["thresholds"]["max_p95_latency_ms"]=919
        self.assertEqual(run(p)["details"]["release_decision"],"hold")

    def test_bad_suite_is_rejected(self):
        for mutator in [lambda p:p.update(cases=[]),lambda p:p["cases"].append(deepcopy(p["cases"][0])),lambda p:p.update(thresholds={"min_quality":float("nan")}),lambda p:p["cases"][0].update(expected_claims=["Not in source"]),lambda p:p.update(cases=p["cases"][:6])]:
            with self.subTest(mutator=mutator):
                p=default_input();mutator(p)
                with self.assertRaises(ValueError):run(p)

    def test_live_candidate_has_no_gold_labels_and_is_checked(self):
        class Context:
            mode="live"
            def __init__(self):self.calls=[]
            def generate_json(self,**kw):
                self.calls.append(kw)
                return dict(answer="Invented answer.",citations=["fake"],refused=False,actions=[])
        ctx=Context();d=run(default_input(),ctx)["details"]
        self.assertEqual(d["live_candidate_calls"],8)
        self.assertEqual(d["release_decision"],"hold")
        self.assertTrue(all(set(c["data"])=={"question","documents"} for c in ctx.calls))

    def test_local_none_is_not_claimed_as_live(self):
        class Context:
            mode="local"
            def generate_json(self,**kw):raise AssertionError("Local mode must not call model")
        self.assertEqual(run(default_input(),Context())["details"]["live_candidate_calls"],0)

    def test_input_is_not_mutated(self):
        p=default_input();before=deepcopy(p);run(p);self.assertEqual(p,before)

    def test_schema_boundaries_reject_invalid_outputs_and_cases(self):
        mutations=[lambda p:p.update(thresholds={"unknown":1}),lambda p:p.update(illustrative_prices={}),lambda p:p["cases"][0].update(question=0),lambda p:p["cases"][0].update(documents=[{}]),lambda p:p["cases"][0]["documents"].append(deepcopy(p["cases"][0]["documents"][0])),lambda p:p["cases"][0].update(expected_claims=["!!!"]),lambda p:p["cases"][0].update(must_refuse=True),lambda p:p["cases"][0].update(expected_claims=[]),lambda p:p["cases"][0].update(candidate={}),lambda p:p["cases"][0]["candidate"].update(refused="false"),lambda p:p["cases"][0]["candidate"].update(citations="policy"),lambda p:p["cases"][0]["candidate"].update(input_tokens=-1),lambda p:p["cases"][0]["candidate"].update(latency_ms=True)]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                p=default_input();mutation(p)
                with self.assertRaises(ValueError):run(p)
        with self.assertRaises(ValueError):run(None)

    def test_live_none_fallback_preserves_fixture_disclosure(self):
        class Context:
            mode="live"
            def generate_json(self,**kw):return None
        d=run(default_input(),Context())["details"]
        self.assertEqual(d["live_candidate_calls"],0)
        self.assertEqual(d["release_decision"],"advance_to_validation")

    def test_invalid_later_case_prevents_all_live_calls(self):
        class Context:
            mode="live"
            def __init__(self):self.calls=0
            def generate_json(self,**kw):self.calls+=1;return None
        p=default_input();p["cases"][-1]["candidate"]["latency_ms"]=-1
        ctx=Context()
        with self.assertRaises(ValueError):run(p,ctx)
        self.assertEqual(ctx.calls,0)
