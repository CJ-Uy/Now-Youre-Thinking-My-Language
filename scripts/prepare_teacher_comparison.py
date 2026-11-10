"""Export locked pilot prompts for chat-export teachers (default: the ten-question screening round); no model calls."""

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

from research import ROOT, core
from research.__main__ import digest, load_data, new_directory, read_json


def prepare_pack(data, output, split="train", start=0, count=10, teachers=("gpt61", "opus55")):
    config_path = ROOT / "configs/pilot.json"
    manifest = load_data(SimpleNamespace(data=data), read_json(config_path))
    if core.data_identity(manifest) != read_json(ROOT / "configs/pilot-data-lock.json"):
        raise ValueError("Teacher comparison requires the locked pilot data")
    problems = core.read_jsonl(data / f"{split}.jsonl")[start:start + count]
    if count < 1 or start < 0 or len(problems) != count:
        raise ValueError(f"Teacher pack requires {count} {split} questions from position {start}")
    template_path = ROOT / "prompts/teacher-comparison-v1.txt"
    template = template_path.read_text(encoding="utf-8")
    output = new_directory(output)
    (output / "prompts").mkdir()
    for teacher in teachers:
        (output / teacher / "raw").mkdir(parents=True)
    core.write_jsonl(output / "inputs.jsonl", problems)
    prompt_files = {}
    for problem in problems:
        name = f"prompts/{problem['id']}.txt"
        prompt = template.replace("{{problem_json}}", json.dumps(problem, ensure_ascii=False))
        with (output / name).open("x", encoding="utf-8", newline="\n") as destination:
            destination.write(prompt)
        prompt_files[name] = digest(output / name)
    core.write_json(output / "manifest.json", {
        "purpose": f"Chat-export teacher prompts for {', '.join(teachers)}: {split} questions {start + 1}-{start + count}",
        "split": split,
        "start": start,
        "status": "prompts prepared; no teacher responses collected",
        "prompt_version": "teacher-comparison-v1",
        "template_sha256": digest(template_path),
        "config_sha256": digest(config_path),
        "data_identity": core.data_identity(manifest),
        "question_ids": [problem["id"] for problem in problems],
        "expected_candidates_per_teacher": 8 * count,
        "inputs_sha256": digest(output / "inputs.jsonl"),
        "prompt_files": prompt_files,
        "instructions": "docs/TEACHER_COMPARISON.md",
    })
    print(f"Prepared {len(problems)} shared prompts at {output}; no teacher calls made.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "artifacts/data/pilot")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--split", choices=("train", "calibration"), default="train")
    parser.add_argument("--start", type=int, default=0, help="0-based position in the saved split")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--teachers", nargs="+", default=["gpt61", "opus55"])
    args = parser.parse_args()
    prepare_pack(args.data, args.output, args.split, args.start, args.count, tuple(args.teachers))
