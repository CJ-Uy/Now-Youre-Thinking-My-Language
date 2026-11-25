# Claude handoff: continue with Opus

Updated 24 October 2026, Asia/Shanghai (UTC+08:00).

**10 November 2026 update:** this page records the state at the 24 October handoff. Since then the Opus teacher collection for the 100-question pilot and 100 calibration questions is complete, and the GPU pipeline was handed to Codex via [prompts/codex-pilot-pipeline.md](../prompts/codex-pilot-pipeline.md). The 10 November entries in the [experiment log](EXPERIMENT_LOG.md) are authoritative for current status; statements below that "no training is authorized" describe 24 October.

## Current decision

The user selected **Opus 5.5 as the single teacher for future research** and will continue in Claude. Preserve the GPT arm as historical screening evidence. The student remains Qwen3-0.6B. The forward design is the original-solution baseline plus the four standard Opus rewrite conditions on identical retained IDs; the nine-condition two-teacher expansion is superseded.

**No training is authorized yet. All 160 candidates remain `reviewed=false`.** Teacher selection does not approve the candidates or authorize bulk generation, API spending, training or public deployment.

Read AGENTS.md, README.md, TEAM_GUIDE.md, final-project-proposal.md and EXPERIMENT_LOG.md before new work. Keep historical course metadata intact.

## Results index

| Result | Report | Private artifacts |
|---|---|---|
| Common validation and scoring | [Teacher screening](pilots/2026-10-24-teacher-screening.md) | artifacts/teacher-comparison/chat-export-round1/common-pipeline-20261024/ |
| Parallel Claude reproduction and model review | Same screening report and experiment log | artifacts/teacher-comparison/chat-export-round1/claude-pipeline-20261024/ |
| Full AI meaning audit and combined human-review queue | [Meaning audit](pilots/2026-10-24-teacher-meaning-audit.md) | artifacts/teacher-comparison/chat-export-round1/meaning-audit-20261024/ |
| Research decisions and run history | [Experiment log](EXPERIMENT_LOG.md) | Saved manifests remain authoritative |
| Original-solution student baseline | [Baseline report](pilots/2026-10-24-original-baseline.md) | artifacts/runs/pilot-original/ and related baseline evaluations |
| Collection procedure and historical comparison | [Teacher protocol](TEACHER_COMPARISON.md) | Prompt pack manifest.json, inputs.jsonl and prompts/ |

## Measured teacher screen

Both teachers produced 80/80 expected candidates for the same ten locked training questions, with 40 per pool. All pass arithmetic/structure checks and preserve exact original equations in order. Each arm has the same 72 feedback-eligible candidates and 144 attempts. The eight one-calculation train-3620 variants per arm have unavailable feedback, not observed zero success.

| Measure | GPT-6.1 | Opus 5.5 |
|---|---:|---:|
| Mean English solution tokens | 62.550 | 60.825 |
| Mean multilingual solution tokens | 64.425 | 61.425 |
| Strict-format student feedback | 83/144 (57.64%) | 86/144 (59.72%) |
| Unparseable final answers | 37 | 36 |
| Runtime errors / truncations | 0 / 0 | 0 / 0 |

Opus's mean material length is 3.72% lower. Its feedback advantage is +2.08 percentage points, with a question-bootstrap 95% interval of -6.25 to +11.11 points. Numeric-only formatting is part of this metric; outputs such as `#### 18 apples.` remain failures. This screening does not establish downstream training benefit or semantic superiority.

Scoring used unchanged Qwen3-0.6B, thinking disabled, a 256-token reasoning budget plus 64 answer tokens, temperature 0.7, top-p 0.8, top-k 20 and matched per-candidate/attempt seeds derived from seed 42. Full continuations, tokenizer measurements, revisions, source hashes and manifests are saved. The separate Claude run reports reproducing all 288 sampled results exactly. Its GPU work overlapped the Codex run, so timings are not comparable.

## Human review and next work

The combined priority queue has **26 unique candidates**: ten specific wording/dependency/terminology flags and sixteen variants sharing one source ambiguity. It combines eight flags from this Codex AI read with two additional flags from the parallel Claude review. All 160 still need human approval; 134 without a specific combined flag are not certified meaning-preserving.

Inspect first:

- GPT train-1458 / multilingual / candidate 3: unsupported, garbled tax wording.
- Opus train-1258 / multilingual / candidate 2: omits the 30-puzzles-per-book dependency while retaining the source's uninformative 450=450 annotation.
- Both arms, every train-3341 variant: the source's third-week phrasing is ambiguous, although every candidate follows the worked solution's week-3 count of 2000. **Decided 24 October 2026 (H-0001):** the user accepted the supplied interpretation (week 3 = 2000, total 9500) and kept the question. Its 16 candidates still need individual decisions.

Human decisions are appended to `artifacts/teacher-comparison/chat-export-round1/human-review-20261024/decisions.jsonl`, separate from raw responses and AI audits.

The full list gives exact candidate keys, raw lines, quotations and the human decision needed. Keep reviewer disagreements visible. Store human decisions separately; do not mark reviewed=true until the user actually approves a candidate. Do not repair first responses or regenerate only flagged candidates.

Before the 100-question Opus collection, fix and record its interface, actual model label, effort and conversation-isolation procedure. Decide with the user whether the ten Opus screening responses are reused under the same procedure or a new collection is made. Multilingual material was not shorter on average under the student tokenizer; the one-calculation prefix exclusion also needs a research decision.

The ten-question screen is not a complete 100-question teacher dataset. Any exclusions must affect the original baseline and all rewrite conditions identically. Do not train, expand generation, calibrate the penalty, open the official test set or publish screening data merely on this handoff. Follow the user's next explicit instruction.

## Portable local bundle

`artifacts/handoff/2026-10-24-opus-teacher-results.zip` contains the complete teacher prompt/raw-output/provenance/scoring/audit pack, including the Claude reproduction, prepared pilot data, relevant documentation/configuration and source files. Extract into a repository root when moving to another clone.

It excludes model weights, environments, caches, original-baseline adapters, personal recordings and unrelated output. It is a teacher-phase handoff, not a backup of every training artifact. The ZIP and artifacts are ignored by Git and require a separate private backup. Nothing was uploaded and the public explainer was not changed.

Original common scoring records commit 2c3cffbd337aaf2cc148b0baef8c42789fcab4f4 and exact research-code/config hashes. The later repository commit 6e7141b adds the parallel comparison utility/review and records the Opus decision. Preserve the existing work rather than reverting it. That utility and its tests were not used or tested by this Codex audit.

Both teachers used shared conversations with different harness instructions and unknown backend snapshots/seeds/costs. This Codex meaning audit was unblinded and in the same conversation that authored GPT outputs. The parallel blind model judgments are still model judgments, not human semantic approval.
