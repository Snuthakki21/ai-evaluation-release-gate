"""Independent Staff review: raw gate precision and reproducible experiment boundaries."""
from copy import deepcopy
import unittest
from app.domain.grading import EvidenceGrader, AggregateStatistics
from app.domain.policy import ReleasePolicy
from app.domain.validation import validate_suite
from projects.ai_release_gate.project import default_input, run

class IndependentProductReview(unittest.TestCase):
    def partial_case(self):
        p=default_input(); c=deepcopy(p['cases'][0])
        c['expected_claims']=['claim '+str(i) for i in range(7)]
        c['documents']=[{'id':'evidence','text':'. '.join(c['expected_claims'])}]
        for key in ('baseline','candidate'):
            c[key].update(answer='. '.join(c['expected_claims'][:6]), citations=['evidence'], refused=False, actions=[])
        return p,c

    def test_quality_gate_uses_raw_fraction_before_presentation(self):
        p,c=self.partial_case(); p['cases'][0]=c
        for case in p['cases'][1:]: case['candidate']=deepcopy(case['baseline'])
        d=run(p)['details']; true_quality=((6/7+0+1+1)/4+sum(r['quality'] for r in d['candidate_cases'][1:]))/len(p['cases'])
        p['thresholds']['min_quality']=true_quality+1e-7
        gate=next(g for g in run(p)['details']['gates'] if g['gate']=='quality')
        self.assertFalse(gate['passed'])

    def test_subcent_cost_precision_is_preserved_for_gate(self):
        p,c=self.partial_case(); c['candidate'].update(input_tokens=1,output_tokens=0)
        row=EvidenceGrader.grade(c,c['candidate'],{'input_per_million':.014,'output_per_million':0})
        aggregate=AggregateStatistics.aggregate([row]); thresholds=dict(validate_suite(p)[1],max_mean_cost_usd=1.2e-8)
        self.assertGreater(aggregate['mean_cost_usd'],thresholds['max_mean_cost_usd'])
        self.assertFalse(next(g for g in ReleasePolicy(thresholds).evaluate(aggregate,aggregate) if g['gate']=='mean_cost_usd')['passed'])

    def test_response_mutation_changes_snapshot_without_changing_suite(self):
        p=default_input(); before=run(p)['details']['experiment_identity']
        p['cases'][0]['candidate']['answer']+=' Extra unsupported statement.'
        after=run(p)['details']['experiment_identity']
        self.assertEqual(before['suite_sha256'],after['suite_sha256'])
        self.assertNotEqual(before['snapshot_sha256']['candidate'],after['snapshot_sha256']['candidate'])
        self.assertNotEqual(before['evaluated_candidate_sha256'],after['evaluated_candidate_sha256'])

    def test_rubric_mutation_changes_suite_identity(self):
        p=default_input(); before=run(p)['details']['experiment_identity']['suite_sha256']
        p['cases'][0]['question']+=' Please cite the source.'
        self.assertNotEqual(before,run(p)['details']['experiment_identity']['suite_sha256'])

    def test_identical_candidates_have_degenerate_zero_paired_interval(self):
        p=default_input()
        for case in p['cases']:case['candidate']=deepcopy(case['baseline'])
        uncertainty=run(p)['details']['uncertainty']
        self.assertEqual(uncertainty['paired_quality_delta'],0)
        self.assertEqual(uncertainty['bootstrap_95_interval'],[0,0])

    def test_invalid_identity_never_calls_provider(self):
        class Context:
            mode='live'
            def generate_json(self,**kwargs):raise AssertionError('provider called')
        p=default_input();p['experiment']={'bootstrap_samples':99}
        with self.assertRaises(ValueError):run(p,Context())
