"""Flag Mandarin use and missing gold intermediates in saved development outputs; no model generation."""

import argparse
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import re
import statistics

from research import ROOT, core
from research.__main__ import DEFAULT_DATA, digest, load_config, load_data, read_json
from scripts.compare_teachers import CJK


LATIN = re.compile(r"[A-Za-z]")
# Unsigned plain numbers only, so "42/2" is not read as the fraction 21 and "10-5" not as -5.
PLAIN_NUMBER = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+")


def mean(values):
    values = [v for v in values if v is not None]
    return statistics.mean(values) if values else None


def gold_intermediates(problem):
    answer = core.numeric(problem["answer"])
    values = set()
    for annotation in re.findall(r"<<([^<>]+)>>", problem["solution"]):
        try:
            value = core.numeric(annotation.rsplit("=", 1)[1])
        except (IndexError, ValueError):
            continue
        if value != answer:
            values.add(abs(value))
    return values


def inspect(prediction, problem):
    output = prediction.get("output") or ""
    han, latin = len(CJK.findall(output)), len(LATIN.findall(output))
    present = {Fraction(n.replace(",", "")) for n in PLAIN_NUMBER.findall(output.partition("####")[0])}
    gold = gold_intermediates(problem)
    missing = sorted(gold - present)
    finished = not prediction["truncated"] and not prediction["error"]
    return {"id": prediction["id"], "budget": prediction["budget"], "correct": prediction["correct"],
            "truncated": prediction["truncated"], "error": prediction["error"],
            "output_tokens": prediction["output_tokens"], "han_characters": han,
            "mandarin_share": han / (han + latin) if han + latin else None,
            "gold_intermediates": len(gold),
            "missing_intermediates": None if prediction["error"] else [str(v) for v in missing],
            "coverage": (len(gold) - len(missing)) / len(gold) if gold and not prediction["error"] else None,
            "lost_step_candidate": bool(missing) and finished and not prediction["correct"],
            "skipped_step_correct": bool(missing) and prediction["correct"]}


def summarize(rows):
    return {"outputs": len(rows), "correct": sum(r["correct"] for r in rows),
            "truncated": sum(r["truncated"] for r in rows),
            "using_mandarin": sum(r["han_characters"] > 0 for r in rows),
            "mean_mandarin_share": mean([r["mandarin_share"] for r in rows]),
            "with_gold_intermediates": sum(r["gold_intermediates"] > 0 for r in rows),
            "mean_coverage": mean([r["coverage"] for r in rows]),
            "full_coverage": sum(r["coverage"] == 1 for r in rows),
            "lost_step_candidates": [r["id"] for r in rows if r["lost_step_candidate"]],
            "skipped_step_correct": [r["id"] for r in rows if r["skipped_step_correct"]]}


def inspect_runs(problems, runs, expected_keys=None):
    lookup = {p["id"]: p for p in problems}
    rows, summaries = [], {}
    for name, predictions in runs.items():
        keys = {(p["id"], p["budget"]) for p in predictions}
        if expected_keys is None:
            expected_keys = keys
        if len(keys) != len(predictions) or keys != expected_keys:
            raise ValueError(f"{name} must have one prediction per expected question ID and budget")
        if any(p["id"] not in lookup for p in predictions):
            raise ValueError(f"{name} has predictions outside the development split")
        inspected = [dict(inspect(p, lookup[p["id"]]), run=name) for p in predictions]
        summaries[name] = {str(b): summarize([r for r in inspected if r["budget"] == b])
                           for b in sorted({r["budget"] for r in inspected})}
        rows += inspected
    return {"summaries": summaries, "rows": sorted(rows, key=lambda r: (r["id"], r["budget"], r["run"]))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "pilot.json")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--run", action="append", required=True, help="NAME=EVALUATION_DIRECTORY; repeat to pair runs")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if any("=" not in spec for spec in args.run):
        parser.error("Give each --run as NAME=EVALUATION_DIRECTORY")
    config = load_config(args.config)
    manifest = load_data(args, config)
    runs, sources = {}, {}
    expected_keys = None
    for name, path in (spec.split("=", 1) for spec in args.run):
        if not name or name in runs:
            parser.error("Give each --run a unique, nonempty name")
        run_manifest = read_json(Path(path) / "manifest.json")
        if run_manifest["data_manifest"] != core.data_identity(manifest):
            raise ValueError(f"{name} was evaluated with different prepared data")
        if run_manifest["split"] != "development":
            raise ValueError("Only development runs are supported; official-test rows do not store gold solutions")
        declared = set(product(run_manifest["question_ids"], run_manifest["budgets"]))
        if expected_keys is not None and declared != expected_keys:
            raise ValueError("Run manifests must cover the same question IDs and budgets")
        expected_keys = declared
        runs[name] = core.read_jsonl(Path(path) / "predictions.jsonl")
        sources[name] = {"directory": str(path), "condition": run_manifest["condition"],
                         "predictions_sha256": digest(Path(path) / "predictions.jsonl")}
    report = inspect_runs(core.read_jsonl(args.data / "development.jsonl"), runs, expected_keys)
    report.update(status="Screening aid: flags choose outputs for human reading; they are not judgments",
                  method=("Mandarin share is Han characters over Han plus Latin letters. Coverage counts gold "
                          "intermediate values from the <<...>> annotations, excluding the final answer, that appear "
                          "as unsigned plain numbers before the first ####. A different valid path, unit or percentage form "
                          "can miss a value without losing a step. Lost-step candidates are finished incorrect "
                          "outputs missing at least one gold intermediate."),
                  runs=sources)
    core.write_json(args.output, report)
    print(json.dumps(report["summaries"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
