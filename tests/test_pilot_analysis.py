import copy
import unittest

from research import core
from scripts import pilot_analysis as analysis
from scripts.pilot_review import render
from test_research import candidate, problem


def repeated(questions=1, agree=0):
    problems, scores2, scores8, attempts2, attempts8 = [], [], [], [], []
    for q in range(questions):
        problems.append(problem(q))
        for pool in core.POOLS:
            for index in range(2):
                row = dict(candidate(pool, index), id=f'train-{q}', validation_errors=[])
                if pool == 'multilingual':
                    row['steps'][0]['text'] = '物品'
                results = []
                for attempt in range(8):
                    winner = 0 if q < agree or attempt < 2 else 1
                    correct = index == winner
                    record = dict(id=row['id'], pool=pool, candidate=index, attempt=attempt,
                                  correct=correct, predicted_answer='17' if correct else '18',
                                  output_tokens=3, output='#### 17' if correct else '#### 18',
                                  truncated=False, error=None, seed=attempt, seconds=1)
                    attempts8.append(record)
                    if attempt < 2:
                        attempts2.append(dict(record, seconds=2))
                    results.append(correct)
                scores2.append(dict(row, feedback_accuracy=sum(results[:2]) / 2))
                scores8.append(dict(row, feedback_accuracy=sum(results) / 8))
    return problems, scores2, scores8, attempts2, attempts8


class AnalysisTests(unittest.TestCase):
    def test_repetition_uses_disjoint_pairs_and_exact_threshold(self):
        result = analysis.stability(*repeated(), 2, 0.1)
        self.assertEqual(result['pairwise_agreement'], 0.5)
        self.assertEqual(result['two_equals_eight'], 0)
        self.assertEqual(result['two_equals_shortest'], 1)
        self.assertEqual(result['training_attempts'], 4)
        boundary = analysis.stability(*repeated(5, 3), 2, 0.1)
        self.assertEqual(boundary['two_equals_eight'], 0.6)
        self.assertEqual(boundary['training_attempts'], 2)

    def test_missing_duplicate_and_nonreproducing_attempts_stop_analysis(self):
        for change in ('missing', 'duplicate', 'output', 'seed', 'tokens'):
            values = repeated()
            attempts = values[4]
            if change == 'missing':
                attempts.pop()
            elif change == 'duplicate':
                attempts.append(attempts[0])
            else:
                field = 'output_tokens' if change == 'tokens' else change
                attempts[0][field] = 'different' if change == 'output' else 99
            with self.subTest(change=change), self.assertRaises(ValueError):
                analysis.stability(*values, 2, 0.1)

    def test_unparseable_and_truncated_attempts_are_retained(self):
        problems, scores, _, attempts, _ = repeated()
        row = next(r for r in attempts if not r['correct'])
        row.update(predicted_answer=None, truncated=True)
        report = analysis.validate_scores(problems, scores, attempts, 2, 2)
        self.assertEqual(report['attempts'], 8)
        self.assertEqual(report['unparseable'], 1)
        self.assertEqual(report['truncated'], 1)

    def test_penalty_requires_both_pools_and_uses_largest_passing_value(self):
        rows = [candidate(pool, i) for pool in core.POOLS for i in range(2)]
        for row in rows:
            row.update(tokens=10 if row['candidate'] == 0 else 40,
                       feedback_accuracy=(0.96 if row['pool'] == 'english' else 0.75) if row['candidate'] == 0 else 1)
            if row['pool'] == 'multilingual':
                row['steps'][0]['text'] = '物品'
        result = analysis.calibrate([problem()], rows, 2)
        self.assertEqual(result['chosen_penalty'], 0.3)
        self.assertEqual(len(result['table']), 7)
        self.assertFalse(result['table'][-1]['passes'])

    def test_stability_tie_break_matches_production_selection(self):
        values = repeated()
        result = analysis.stability(*values, 2, 0.1)
        groups, _ = core.select_conditions(values[0], values[2], 2, 0.1)
        for pick in result['picks']:
            self.assertEqual(pick['eight'], groups[pick['pool'] + '-feedback'][0]['candidate'])


class ReviewTests(unittest.TestCase):
    def test_deduplicates_escapes_and_preserves_blank_decisions(self):
        row = candidate('multilingual')
        row['steps'][0]['text'] = '<script>物品</script>'
        groups = {'multilingual-shortest': [row], 'multilingual-feedback': [copy.deepcopy(row)]}
        template = '<ol><li>Approve (A), Reject (R), Unsure (U).</li></ol><h2>Check these first</h2><p>0-M0</p><h2>train-0</h2>'
        hints = [{'candidate': '0-M0', 'decision': 'R', 'reason': 'unclear', 'disagrees_with_note': False}]
        ledger = [{'scope': 'note', 'refers_to': ['H-2']},
                  dict(row, scope='candidate', arm='opus55', decision_id='H-2', decision='approve', rationale='gloss')]
        text, picks = render([problem()], groups, 'multilingual', template, hints, ledger)
        self.assertEqual(picks, ['0-M0'])
        self.assertEqual(text.count('<tr><td>0-M0</td>'), 1)
        self.assertNotIn('<script>', text)
        self.assertIn('&lt;script&gt;', text)
        self.assertIn('needs bilingual confirmation', text)
        self.assertIn('Fable AI pre-review (not human): R', text)
        self.assertIn('<td></td></tr>', text)
        self.assertIn('shortest, feedback', text)


if __name__ == '__main__':
    unittest.main()
