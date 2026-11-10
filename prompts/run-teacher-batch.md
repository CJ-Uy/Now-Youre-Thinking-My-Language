# Opus teacher batch instruction (pilot collection, 10 November 2026)

Each ten-question batch of the 100-question pilot and calibration collection was given to a fresh Claude Code subagent (Agent tool, model override `opus`) with this instruction. `ROOT`, `BATCH` and `QUESTIONS` were filled in per batch; nothing else changed. Prompt packs come from `scripts/prepare_teacher_comparison.py --teachers opus55` and use the unchanged `teacher-comparison-v1` template. One conversation handles ten prompts, as in the round-1 screening collection.

```text
You are a teacher generating compact training solutions for our Qwen3-0.6B study.
ARM=opus55
ROOT={ROOT}
BATCH={BATCH}
QUESTIONS={QUESTIONS}

Your task is only to produce this teacher arm's candidate solutions for the ten question IDs in QUESTIONS. Do not change code, prompts, configuration or datasets, run training/evaluation/scoring, or read any other batch's or teacher's outputs. Do not call another model, start subagents, or use web search to generate the solutions.

Read ROOT/manifest.json. Check with Python (hashlib) that each ROOT/prompts/<id>.txt for your ten IDs exists and its sha256 equals the manifest's prompt_files entry. Then read your ten prompt files. If the pack is missing, a hash differs, or your own system context does not say you are Opus 5.5, report that and stop; do not substitute questions or models.

For each prompt, follow its instructions exactly. Produce all eight candidates yourself: four English and four multilingual, numbered 0-3 within each pool. Keep reviewed=false. Preserve the supplied calculations, quantities, meaning and final answer. Do not add or remove steps to obtain a shorter solution.

Save your complete first response to each prompt as UTF-8 JSONL in ROOT/opus55/raw/<id>.jsonl with your file-writing tool, one JSON object per line and no Markdown fences. That file is the response. Do not overwrite existing files. Do not edit, repair or regenerate a response after writing it. If you cannot complete a question, write the failure to ROOT/opus55/raw/<id>.FAILED.txt and report the missing candidates rather than inventing them.

After all ten files are written, run one format check with Python and report its result without changing any file: each line parses as JSON; exactly the eight (pool, candidate) keys; fields id, pool, candidate, steps, answer, reviewed; each step's equation equals the source's <<...>> annotations in order (read sources from ROOT/inputs.jsonl); answer equals the source answer; no "####", chat control tokens or thinking tags in step text; English-pool text is ASCII-only.

Create ROOT/opus55/PROVENANCE-batch-{BATCH}.md recording:
- the model label and model ID exactly as your own system context states them (quote them);
- interface: Claude Code subagent started by the Agent tool from a parent Opus 5.5 session, model override "opus";
- date/time with timezone (run `date`);
- reasoning/effort settings visible to you, else "unknown";
- any session-level instructions you can see besides this task (for example CLAUDE.md content, output-style or hook text): name them briefly, do not copy them;
- that your ten prompts were handled in one subagent conversation, and you read all ten before writing;
- each prompt file and response file with sha256;
- failures and retries (there should be no retries);
- backend snapshot, seed, token usage and cost: unknown unless shown to you.

Do not mark anything human-reviewed. When finished, report the files created, candidate count, format-check result and missing/failed question IDs.
```
