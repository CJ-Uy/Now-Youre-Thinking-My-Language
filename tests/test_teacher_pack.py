import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from research import ROOT, core
from research.__main__ import digest
from scripts.compare_teachers import compare_arms
from scripts.prepare_teacher_comparison import prepare_pack


def scored(question, pool, index, tokens, accuracy, text="Items"):
    return {"id": f"train-{question}", "pool": pool, "candidate": index, "answer": "17", "reviewed": False,
            "steps": [{"text": text, "equation": "3*5=15"}, {"text": "Total", "equation": "15+2=17"}],
            "validation_errors": [], "tokens": tokens, "feedback_accuracy": accuracy}


class TeacherComparisonTests(unittest.TestCase):
    def test_arms_are_paired_only_on_questions_both_teachers_can_supply(self):
        problems = [{"id": f"train-{i}", "question": "Q?", "solution": "<<3*5=15>>15 <<15+2=17>>17\n#### 17", "answer": "17"}
                    for i in range(2)]
        first = [scored(q, "english", 0, 20, 0.5) for q in range(2)] + [scored(q, "english", 1, 30, 1.0) for q in range(2)]
        first += [scored(q, "multilingual", i, 18, 0.0, "物品") for q in range(2) for i in range(2)]
        second = [scored(q, "english", 0, 16, 0.0) for q in range(2)] + [scored(q, "english", 1, 40, 1.0) for q in range(2)]
        second += [scored(q, "multilingual", i, 15, 1.0) for q in range(2) for i in range(2)]
        for row in second[-2:]:
            row["feedback_error"] = "Partial solution reveals the final answer"
        report = compare_arms(problems, {"a": first, "b": second}, {"train-0": 40, "train-1": 40}, 2, 0.1)
        self.assertEqual(report["common_selected_ids"], ["train-0"])
        self.assertEqual(report["arms"]["b"]["excluded"][0]["id"], "train-1")
        self.assertEqual(report["arms"]["a"]["pools"]["multilingual"]["with_chinese_text"], 4)
        self.assertEqual(report["arms"]["a"]["pools"]["english"]["mean_tokens_vs_original"], 0.625)
        self.assertEqual(report["arms"]["b"]["pools"]["multilingual"]["feedback_eligible"], 2)
        self.assertEqual(report["paired"]["english-shortest"]["mean_token_difference"], -4)
        self.assertEqual(report["paired"]["english-feedback"]["mean_token_difference"], 10)
        self.assertEqual(report["paired"]["english-feedback"]["a_shorter"], 1)
        self.assertEqual(len(report["per_question"]), 4)


class TeacherPackTests(unittest.TestCase):
    def fixture(self, root):
        (root / "configs").mkdir()
        (root / "prompts").mkdir()
        (root / "prompts/teacher-comparison-v1.txt").write_text(
            (ROOT / "prompts/teacher-comparison-v1.txt").read_text(encoding="utf-8"), encoding="utf-8")
        data = root / "data"
        data.mkdir()
        rows = [{"id": f"train-{i}", "question": f"Question {i}?", "solution": "<<2+3=5>>\n#### 5", "answer": "5"}
                for i in range(12)]
        core.write_jsonl(data / "train.jsonl", rows)
        config = {"model": "student", "dataset": "task"}
        manifest = {**config, "model_revision": "model-sha", "dataset_revision": "data-sha",
                    "dataset_config": "main", "seed": 42, "sizes": {"train": 12},
                    "ids": {"train": [row["id"] for row in rows]},
                    "files": {"train.jsonl": digest(data / "train.jsonl")}}
        core.write_json(data / "manifest.json", manifest)
        core.write_json(root / "configs/pilot.json", config)
        core.write_json(root / "configs/pilot-data-lock.json", core.data_identity(manifest))
        return data, rows

    def test_identical_pack_inputs_and_prompts_are_hashed_and_existing_work_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, rows = self.fixture(root)
            output = root / "pack"
            with patch("scripts.prepare_teacher_comparison.ROOT", root):
                prepare_pack(data, output)
                with self.assertRaisesRegex(ValueError, "already exists"):
                    prepare_pack(data, output)
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(core.read_jsonl(output / "inputs.jsonl"), rows[:10])
            self.assertEqual(manifest["question_ids"], [row["id"] for row in rows[:10]])
            self.assertEqual(manifest["expected_candidates_per_teacher"], 80)
            self.assertEqual(len(manifest["prompt_files"]), 10)
            for name, sha in manifest["prompt_files"].items():
                self.assertEqual(digest(output / name), sha)
                text = (output / name).read_text(encoding="utf-8")
                self.assertNotIn("{{problem_json}}", text)
                self.assertIn('"solution": "<<2+3=5>>\\n#### 5"', text)

    def test_changed_split_is_rejected_before_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, _ = self.fixture(root)
            with (data / "train.jsonl").open("a", encoding="utf-8") as target:
                target.write("{}\n")
            with patch("scripts.prepare_teacher_comparison.ROOT", root):
                with self.assertRaisesRegex(ValueError, "Prepared split changed"):
                    prepare_pack(data, root / "pack")
            self.assertFalse((root / "pack").exists())

    def test_different_locked_revision_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data, _ = self.fixture(root)
            manifest = json.loads((data / "manifest.json").read_text(encoding="utf-8"))
            manifest["dataset_revision"] = "different"
            (data / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with patch("scripts.prepare_teacher_comparison.ROOT", root):
                with self.assertRaisesRegex(ValueError, "locked pilot"):
                    prepare_pack(data, root / "pack")
            self.assertFalse((root / "pack").exists())


if __name__ == "__main__":
    unittest.main()
