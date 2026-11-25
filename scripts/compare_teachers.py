"""Compare two scored teacher arms on matched questions; no model generation."""

import argparse
import json
from pathlib import Path
import re
import statistics

from research import ROOT, core
from research.__main__ import DEFAULT_DATA, digest, load_config, load_data, read_json


CJK = re.compile(r"[㐀-鿿]")


def mean(values):
    return statistics.mean(values) if values else None


def arm_summary(problems, scored, original_tokens, per_pool, penalty):
    selected, excluded = core.select_conditions(problems, scored, per_pool, penalty)
    pools = {}
    for pool in core.POOLS:
        rows = [c for c in scored if c["pool"] == pool]
        valid = [c for c in rows if not c["validation_errors"]]
        eligible = [c for c in valid if not c.get("feedback_error")]
        pools[pool] = {"candidates": len(rows), "arithmetic_valid": len(valid), "feedback_eligible": len(eligible),
                       "with_chinese_text": sum(any(CJK.search(s["text"]) for s in c["steps"]) for c in rows),
                       "mean_tokens": mean([c["tokens"] for c in valid]),
                       "mean_tokens_vs_original": mean([c["tokens"] / original_tokens[c["id"]] for c in valid]),
                       "mean_feedback_accuracy": mean([c["feedback_accuracy"] for c in eligible])}
    return {"pools": pools, "selected_questions": len(selected["original"]), "excluded": excluded}, selected


def compare_arms(problems, arms, original_tokens, per_pool, penalty):
    first, second = arms
    summaries, selections = {}, {}
    for name, scored in arms.items():
        summaries[name], selections[name] = arm_summary(problems, scored, original_tokens, per_pool, penalty)
    ids = sorted(set.intersection(*({r["id"] for r in s["original"]} for s in selections.values())))
    paired, per_question = {}, []
    for condition in core.CONDITIONS[1:]:
        a, b = ({r["id"]: r for r in selections[name][condition]} for name in arms)
        differences = [b[i]["tokens"] - a[i]["tokens"] for i in ids]
        paired[condition] = {"questions": len(ids), "mean_token_difference": mean(differences),
                             f"{first}_shorter": sum(d > 0 for d in differences),
                             f"{second}_shorter": sum(d < 0 for d in differences),
                             "ties": sum(d == 0 for d in differences),
                             "mean_feedback_accuracy_difference": mean([b[i]["feedback_accuracy"] - a[i]["feedback_accuracy"] for i in ids])}
        for i in ids:
            per_question.append({"id": i, "condition": condition, "original_tokens": original_tokens[i],
                                 **{f"{name}_{field}": row[i][field] for name, row in ((first, a), (second, b))
                                    for field in ("candidate", "tokens", "feedback_accuracy")}})
    return {"arms": summaries, "common_selected_ids": ids,
            "original_mean_tokens": mean([original_tokens[i] for i in ids]),
            "differences": f"{second} minus {first}", "paired": paired, "per_question": per_question}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "pilot.json")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--arm", action="append", required=True, help="NAME=SCORE_DIRECTORY; give exactly two")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if len(args.arm) != 2 or any("=" not in spec for spec in args.arm):
        parser.error("Give exactly two --arm NAME=SCORE_DIRECTORY values")
    config = load_config(args.config)
    manifest = load_data(args, config)
    arms, manifests, sources = {}, {}, {}
    for name, path in (spec.split("=", 1) for spec in args.arm):
        manifests[name] = read_json(Path(path) / "manifest.json")
        if manifests[name]["data_manifest"] != core.data_identity(manifest) or manifests[name]["config"] != config:
            raise ValueError(f"{name} was scored with different prepared data or configuration")
        arms[name] = core.read_jsonl(Path(path) / "scored.jsonl")
        sources[name] = digest(Path(path) / "scored.jsonl")
    first, second = manifests.values()
    if first["split"] != second["split"] or first["attempts"] != second["attempts"]:
        raise ValueError("Teacher arms were scored on different splits or attempt counts")
    keys = [{(c["id"], c["pool"], c["candidate"]) for c in rows} for rows in arms.values()]
    if keys[0] != keys[1]:
        raise ValueError("Teacher arms must contain the same question, pool and candidate slots")
    ids = {key[0] for key in keys[0]}
    problems = [p for p in core.read_jsonl(args.data / f"{first['split']}.jsonl") if p["id"] in ids]

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(config["model"], revision=manifest["model_revision"], local_files_only=True)
    original_tokens = {p["id"]: len(tokenizer.encode(p["solution"], add_special_tokens=False)) for p in problems}
    report = compare_arms(problems, arms, original_tokens, config["candidates_per_pool"], config["length_penalty"])
    report.update(status="Screening only: candidates are not human-reviewed and feedback uses few attempts",
                  split=first["split"], attempts=first["attempts"], length_penalty=config["length_penalty"],
                  scored_sha256=sources)
    core.write_json(args.output, report)
    print(json.dumps({key: report[key] for key in ("arms", "common_selected_ids", "original_mean_tokens", "paired")}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
