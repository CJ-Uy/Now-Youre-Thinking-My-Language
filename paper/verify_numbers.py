"""Recompute the numbers the paper reports from the saved predictions and comparisons.

Needs the local, ignored artifacts of the course run and the laptop quick decode.
Writes paper/verified.json, which build_paper.js and figure3.py read. Raw model
outputs stay in artifacts/ and are not copied into that file.

Usage: .venv/Scripts/python.exe paper/verify_numbers.py
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")
root = Path(__file__).resolve().parents[1]
school = root / "artifacts/handoff/2026-11-21-opus55-aiassist-school-results"
CONDS = ["unchanged", "original", "english-shortest", "english-feedback", "multilingual-shortest", "multilingual-feedback"]
HAN = re.compile(r"[一-鿿]")
LATIN = re.compile(r"[A-Za-z]")


def load(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


runs = {c: load(school / f"artifacts/runs/{c}-dev/predictions.jsonl") for c in CONDS}
out = {"appendix_a": [], "appendix_b": [], "quick": {}, "identical_across_budgets": {}, "han": {}, "examples": {}}

print("== Appendix A (recomputed from predictions, checked against summary.json)")
for budget in (128, 256, 512):
    for c in CONDS:
        rows = [r for r in runs[c] if r["budget"] == budget]
        n = len(rows)
        correct = sum(bool(r["correct"]) for r in rows)
        tokens = sum(r["output_tokens"] for r in rows) / n
        seconds = sum(r["seconds"] for r in rows) / n
        unpar = sum(r["predicted_answer"] in (None, "") for r in rows)
        trunc = sum(bool(r["truncated"]) for r in rows)
        errors = sum(r["error"] is not None for r in rows)
        summ = next(s for s in json.loads((school / f"artifacts/runs/{c}-dev/summary.json").read_text(encoding="utf-8"))["results"] if s["budget"] == budget)
        agree = summ["correct"] == correct and abs(summ["mean_output_tokens"] - tokens) < 1e-6 and summ["truncated"] == trunc
        row = [budget, c, n, correct, round(100 * correct / n, 1), round(tokens, 2), round(seconds, 2), unpar, trunc, errors]
        out["appendix_a"].append(row)
        print(row, "summary_agrees" if agree else f"SUMMARY_DIFFERS {summ}")

print("== Appendix B (from control/*.json)")
PAIRS = [("english-shortest", "multilingual-shortest"), ("english-feedback", "multilingual-feedback"), ("original", "english-shortest"), ("original", "english-feedback"), ("original", "multilingual-shortest"), ("original", "multilingual-feedback"), ("unchanged", "original")]
for budget in (128, 256, 512):
    for ref, cand in PAIRS:
        res = next(r for r in json.loads((school / f"control/{ref}-to-{cand}.json").read_text(encoding="utf-8"))["results"] if r["budget"] == budget)
        lo, hi = res["accuracy_difference_95_ci"]
        ref_rows = {r["id"]: r for r in runs[ref] if r["budget"] == budget}
        cand_rows = {r["id"]: r for r in runs[cand] if r["budget"] == budget}
        diff = 100 * (sum(bool(r["correct"]) for r in cand_rows.values()) - sum(bool(r["correct"]) for r in ref_rows.values())) / len(ref_rows)
        red = 100 * (1 - sum(r["output_tokens"] for r in cand_rows.values()) / sum(r["output_tokens"] for r in ref_rows.values()))
        row = [budget, ref, cand, round(100 * res["accuracy_difference"], 1), round(100 * lo, 1), round(100 * hi, 1), round(100 * res["token_reduction"], 1), res["sample_size"], res["bootstrap_samples"], res["seed"]]
        out["appendix_b"].append(row)
        print(row, "recomputed", round(diff, 1), round(red, 1))

print("== Laptop quick decode vs course run on the same question IDs, budget 256")
order = [r["id"] for r in runs["unchanged"] if r["budget"] == 256]
for c in CONDS:
    quick = load(root / f"artifacts/runs/opus55-aiassist-laptop-{c}-quick/predictions.jsonl")
    ids = [r["id"] for r in quick]
    course = {r["id"]: r for r in runs[c] if r["budget"] == 256}
    same_text = sum(course[i]["output"] == r["output"] for i, r in zip(ids, quick))
    info = {"n": len(quick), "budgets": sorted({r["budget"] for r in quick}), "first50_of_course_order": ids == order[:50], "laptop_correct": sum(bool(r["correct"]) for r in quick), "course_correct": sum(bool(course[i]["correct"]) for i in ids), "identical_outputs": same_text, "seeds_match": all(course[i]["seed"] == r["seed"] for i, r in zip(ids, quick))}
    out["quick"][c] = info
    print(c, info)

print("== Share of questions with identical output text at all three budgets")
for c in CONDS:
    by_id = {}
    for r in runs[c]:
        by_id.setdefault(r["id"], {})[r["budget"]] = r["output"]
    same = sum(len(set(v.values())) == 1 for v in by_id.values())
    out["identical_across_budgets"][c] = [same, len(by_id)]
    print(c, same, "of", len(by_id))

print("== Han characters at budget 256")
for c in CONDS:
    rows = [r for r in runs[c] if r["budget"] == 256]
    han = sum(bool(HAN.search(r["output"])) for r in rows)
    both = sum(bool(HAN.search(r["output"])) and bool(LATIN.search(r["output"])) for r in rows)
    out["han"][c] = [han, both]
    print(c, "han", han, "han_and_latin", both)

print("== Example questions at budget 256")
for qid in ("train-4978", "train-5952", "train-6304"):
    for c in CONDS:
        r = next(r for r in runs[c] if r["budget"] == 256 and r["id"] == qid)
        out["examples"][f"{qid}/{c}"] = {"tokens": r["output_tokens"], "predicted": r["predicted_answer"], "correct": r["correct"]}
        print(qid, c, r["output_tokens"], repr(r["predicted_answer"]), r["correct"])

Path(__file__).with_name("verified.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
