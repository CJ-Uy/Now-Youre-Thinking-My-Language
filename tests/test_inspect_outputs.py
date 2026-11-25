import unittest

from scripts.inspect_outputs import inspect_runs


class OutputInspectionTests(unittest.TestCase):
    problem = {"id": "a", "solution": "<<1+2=3>> <<3+1=4>> <<3+4=7>>", "answer": "7"}
    prediction = {"id": "a", "budget": 128, "output": "合A 3\n#### 4\n#### 7",
                  "output_tokens": 12, "correct": False, "error": None, "truncated": False}

    def test_reasoning_coverage_stops_at_first_answer_marker(self):
        runs = {"wrong": [self.prediction], "correct": [dict(self.prediction, correct=True)],
                "truncated": [dict(self.prediction, truncated=True)]}
        report = inspect_runs([self.problem], runs)
        correct, truncated, wrong = report["rows"]
        self.assertEqual(wrong["mandarin_share"], 0.5)
        self.assertEqual(wrong["coverage"], 0.5)
        self.assertEqual(wrong["missing_intermediates"], ["4"])
        self.assertTrue(wrong["lost_step_candidate"])
        self.assertTrue(correct["skipped_step_correct"])
        self.assertFalse(truncated["lost_step_candidate"])

    def test_failed_generation_stays_in_count_with_unknown_measurements(self):
        failed = dict(self.prediction, output="", error="generation failed", output_tokens=None)
        report = inspect_runs([self.problem], {"model": [failed]})
        self.assertEqual(report["summaries"]["model"]["128"]["outputs"], 1)
        row = report["rows"][0]
        for field in ("output_tokens", "mandarin_share", "coverage", "missing_intermediates"):
            self.assertIsNone(row[field])
        self.assertFalse(row["lost_step_candidate"])

    def test_rejects_duplicate_and_incomplete_prediction_pairs(self):
        with self.assertRaises(ValueError):
            inspect_runs([self.problem], {"left": [self.prediction], "right": [self.prediction] * 2})
        with self.assertRaises(ValueError):
            inspect_runs([self.problem], {"model": [self.prediction]}, {("a", 128), ("a", 256)})
