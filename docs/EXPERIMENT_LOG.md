# Experiment and decision log

Keep this file in Git so both researchers can see why the current settings were chosen. Preserve earlier entries and identify superseded decisions explicitly. Put bulk outputs in the ignored artifact archive, not in this document.

## 24 October 2026: repository setup

- Added the Python experiment pipeline, pilot config, local environment setup, tests and teammate documentation alongside the existing explainer.
- Starting settings follow the final proposal; default hyperparameters and the length penalty remain provisional.
- Setup verification is recorded in [SETUP_VERIFICATION.md](SETUP_VERIFICATION.md). Smoke checks are infrastructure checks, not evidence for multilingual compression.
- No teacher has been selected by setup, no human semantic review has been claimed, and no full five-condition or final-test result has been established.
- Next research action: run and profile the original-solution pilot baseline, then choose the student/teacher and test a small rewrite batch.

## 24 October 2026: original-solution pilot started

- User authorized the 100-question pilot and full original-solution baseline training.
- Source snapshot: `ab2747cbad821a739e47a69c34463d33b2336e9a`; no changes to the training code or pilot configuration for this run.
- Prepared input identity matches `configs/pilot-data-lock.json`. Audited 100 training, 300 calibration and 200 development IDs: all disjoint, split hashes verified, and all gold final answers parse correctly.
- Training uses the original supplied solutions, seed 42, three epochs, LoRA rank 8, batch size 1 and accumulation 8. Output: `artifacts/runs/pilot-original/`.
- Initial plan: unchanged Qwen3-0.6B versus the original-solution adapter on all 200 development questions at reasoning budgets 128, 256 and 512. Superseded for this run by the user's explicit quick scope: the first 50 saved development questions, budget 256 plus up to 64 answer tokens. The full sweep is deferred; official test examples remain reserved.
- Laptop observed on AC power with Legion Performance Mode; sampled hardware readings are retained in the training artifact directory. Timing remains specific to this hardware and its operating conditions.
- Teacher decision: the user wants GPT-6.1 versus Opus 5.5 generating rewritten training solutions, with outputs imported from their ChatGPT and Claude accounts. The shared ten-question [protocol and prompt pack](TEACHER_COMPARISON.md) keep the datasets separate. Later teacher-specific student adapters must use matched IDs/settings. No teacher output was used in the original baseline, and no hosted teacher calls were made.
- Training completed: three epochs, 39 optimizer updates, 188.1652 seconds of Trainer runtime, peak PyTorch-allocated VRAM 2,032,115,712 bytes. Final adapter and `run.json` are saved; this is a full pilot training run, not a smoke check.
- Development evaluation is in progress. Current status and completed measurements: [pilot report](pilots/2026-10-24-original-baseline.md). Evaluation results will be entered only after their artifacts confirm completion.
- Unchanged quick reference completed 50/50: 18 correct, mean 128.38 output tokens, zero runtime errors, one truncation and 19 unparseable final answers. The original adapter is now evaluating the same questions. Accuracy includes strict final-answer formatting; the pilot report records an example and this interpretation limit.
- Teacher handoff: the user will open the repository with Opus. Added a [shared repository-assistant instruction](../prompts/run-teacher-comparison.md), with only the output arm changed for a fresh GPT-6.1 session. Keep the same conversation-isolation procedure for both teachers; record any UI/backend settings that cannot be controlled as unknown. Prompt-pack hashes and first-ten locked training IDs were verified, and all 30 Python tests pass.

## 24 October 2026: Opus ten-question outputs checked

- User ran the repository prompt in Opus and asked for a completion check. Found all ten expected response files and the provenance record in `artifacts/teacher-comparison/chat-export-round1/opus55/`.
- Independent audit: 80 unique expected candidates, 40 per language pool, 80 arithmetic/structure passes, exact source equations in original order, unchanged final answers, prompt/input hashes verified and all `reviewed` flags false. Import into `artifacts/rewrites/teacher-opus55-round1/` completed successfully. No responses were rewritten or repaired during this check.
- Provenance records a single Claude Code conversation with reported Opus 5.5 label, custom session instructions, and unknown backend snapshot/seed/billing. GPT should use the same shared-conversation procedure; capture any differing session instructions.
- GPT raw response directory has no JSONL response files yet. Human meaning review, student feedback, token comparison and downstream training remain pending. The [screening report](pilots/2026-10-24-teacher-screening.md) records evidence and limits; raw data stays local and ignored.
- Static prefix eligibility accepts 72/80 candidates. All eight `train-3620` candidates correctly preserve a one-calculation source and therefore cannot supply an intermediate-only prefix under the current feedback policy. This check performs no student generations; GPT must follow the same eligibility rule.

## 24 October 2026: quick original-baseline comparison completed

- Both serial evaluations exited successfully with 50 predictions each, using budget 256 plus up to 64 answer tokens. Compared unchanged Qwen3-0.6B against the full 100-question original-solution adapter. No training/evaluation code or pilot configuration was changed.
- Strict formatted-answer accuracy: 18/50 (36%) versus 24/50 (48%). Paired difference +12 percentage points, question-bootstrap 95% interval −4 to +28 points; 2,000 bootstrap samples, seed 42. This does not establish an improvement across training seeds.
- Mean output tokens: 128.38 versus 115.24, a 10.24% reduction. Mean generation seconds: 13.8091 versus 21.3756, about 55% slower with the current unmerged-adapter runtime. Zero runtime errors and one truncated output in each arm.
- Unparseable final answers fell from 19 to one. Eight of the 12 newly correct outputs had unparseable reference answers, so the observed accuracy change cannot be described as a pure arithmetic-reasoning gain.
- Comparison and separate pairing/format audit: `artifacts/runs/pilot-quick-baseline-comparison.json` and `artifacts/runs/pilot-quick-baseline-audit.json`. Matching IDs, gold answers, seeds, prompt-token counts and full evaluation manifests were verified. The [pilot report](pilots/2026-10-24-original-baseline.md) contains the completed table and reproduction commands.
- The full 200-question/three-budget sweep, official test, additional training seeds, merged-adapter benchmarking, GPT teacher collection and teacher-specific training remain unrun. Raw artifacts remain local and ignored; the procedure and aggregate findings are tracked for the team.

## 24 October 2026: matched teacher validation and feedback scoring

- User authorized common-pipeline validation, student-feedback scoring and comparison of both teacher arms, with raw responses preserved, every `reviewed` flag false and no training.
- Fresh run directory: `artifacts/teacher-comparison/chat-export-round1/common-pipeline-20261024/`. Earlier Opus imports and audits are preserved.
- Preflight verified the locked pilot identity, first ten training IDs, input/prompt hashes, 80 unique candidates per arm and unchanged original equations in order. Fresh `research rewrite --limit 10 --import-file ...` imports accepted all 80 candidates from each teacher.
- Both arms have 72 feedback-eligible candidates. The eight `train-3620` candidates in each arm have one annotated calculation and cannot supply an intermediate prefix; they remain in the records, with feedback unavailable.
- Scoring uses unchanged Qwen3-0.6B, two attempts per eligible candidate, matched ID/pool/index/attempt seeds, thinking disabled, reasoning budget 256 and answer budget 64. Arms run serially, GPT first; no competing GPU research workload was observed before starting.
- GPT's `train-1458`, multilingual candidate 3, retains its known unsolicited tax wording. It passes mechanical validation and remains in this unreviewed screening run; the flag is not erased or treated as human approval.
- Both scoring processes completed successfully with 144 attempts and 80 scored candidates each. GPT finished at 06:05:03 +08:00 and Opus at 06:16:15 +08:00. There were no runtime errors, truncations or missing token measurements. Unparseable final answers: GPT 37, Opus 36; these remain incorrect under the shared numeric-only answer rule.
- GPT strict feedback success: English 36/72, multilingual 47/72, total 83/144 (57.64%). Opus: English 36/72, multilingual 50/72, total 86/144 (59.72%). GPT-minus-Opus paired question-bootstrap difference is -2.08 percentage points, 95% interval -11.11 to +6.25; nine eligible question units, 2,000 resamples, seed 42. This screening does not establish a teacher winner.
- Mean full-solution Qwen tokens: GPT English 62.550, multilingual 64.425; Opus English 60.825, multilingual 61.425. Across both pools Opus's mean is 3.72% lower in this collection. These are unreviewed teaching-material lengths, not trained-student token reductions.
- Final assertions verified all raw/provenance hashes unchanged, matching score manifests and paired attempt seeds, candidate contents preserved through import/scoring, all review flags false and independent tokenizer counts. Research-code/config hashes are recorded and unchanged; both manifests identify commit `2c3cffbd337aaf2cc148b0baef8c42789fcab4f4` with a dirty working tree. Concurrent comparison-utility and test edits observed at handoff were left untouched, were not used and were not tested by this run.
- Completed measurements, per-question results, format examples, collection/hardware limits and reproduction paths are in the [screening comparison](pilots/2026-10-24-teacher-screening.md). Machine-readable results: `common-pipeline-20261024/comparison.json` under the prompt pack. No teacher-specific training, condition selection, calibration tuning or official-test evaluation ran. Human meaning review remains pending.

## 24 October 2026: independent teacher reproduction and blind model review

- The user asked a separate Claude session to repeat validation and scoring independently, audit meaning and wording, and report which teacher is better. Raw responses were preserved, every `reviewed` flag stayed false and no training ran. Output: `artifacts/teacher-comparison/chat-export-round1/claude-pipeline-20261024/`.
- Each arm was consolidated again from its raw files. The rows equal the Codex run's sources apart from order. Both imports accepted 80/80 candidates.
- Scoring was repeated with the same command and configuration. All 144 attempts per arm match the Codex run in seed, predicted answer and output-token count. Every candidate's token count, feedback accuracy and feedback error also match. The two runs overlapped on the GPU, so their timings are not comparable.
- Added `scripts/compare_teachers.py` and a regression test. The script applies the pipeline's selection rule, with the provisional penalty 0.1, to each arm. It then pairs the selected candidates on the questions both arms retain: the same nine questions for both teachers. `train-3620` is excluded from every condition because a one-calculation question cannot supply a feedback prefix.
- Selected training material is shorter for Opus in all four rewritten conditions: by 0.78 to 2.67 mean tokens, and on five or six of the nine questions. Selected feedback accuracy favours GPT in both English conditions (+0.22 for shortest, +0.11 for feedback) and is equal in both multilingual conditions. With two attempts per candidate, these differences are noisy.
- Blind model review: Claude Sonnet and Claude Opus subagents independently judged all 160 candidates. Each saw only an anonymized sheet with shuffled codes; the teacher key was stored outside their directory. Verdicts agreed on 157/160. Both reviewers rejected GPT `train-1458` multilingual 3, which has invented pre-tax wording that GPT had already flagged itself. Four other candidates are flagged for human review; see the [screening report](pilots/2026-10-24-teacher-screening.md). Model review is not human review, and one reviewer shares the Opus teacher's model family.
- Reading of this screen: Opus is marginally preferable, being slightly shorter and having no rejected candidate. No difference is established, however; every interval in the Codex comparison includes zero. The downstream student comparison remains the deciding test.
- Two observations need recorded decisions before the 100-question round. First, multilingual candidates are not shorter than English ones under the Qwen tokenizer for either teacher (mean tokens: Opus 61.4 versus 60.8, GPT 64.4 versus 62.6). Second, the current prefix rule excludes every one-calculation question from all five conditions.

## 24 October 2026: teacher decision, Opus 5.5

- Question decided: which hosted model generates rewritten training solutions for the 100-question pilot and later rounds.
- Evidence: the ten-question screening round, in `common-pipeline-20261024/` and `claude-pipeline-20261024/` under `artifacts/teacher-comparison/chat-export-round1/`, and the [screening report](pilots/2026-10-24-teacher-screening.md).
- Decision: the user chose **Opus 5.5 as the single teacher**. The Codex (GPT-6.1) analysis and the Claude (Opus 5.5) analysis each recommended Opus. GPT's own analysis recommending Opus is the less self-interested of the two.
- Reason: both teachers had equal mechanical validity (80/80) and feedback eligibility (72/80). Opus material was slightly shorter (61.1 versus 63.5 mean Qwen tokens) and had similar feedback success (86 versus 83 of 144). No Opus candidate was rejected in the blind model review, against one GPT rejection. Every difference is within screening uncertainty, so this is a practical choice. It is not evidence that Opus-trained students will perform better.
- Alternatives considered: GPT-6.1 alone, and keeping both teachers with the nine-condition teacher-specific training design.
- Protocol change: the teacher-specific downstream comparison is dropped. The study returns to the proposal's five matched conditions, with Opus 5.5 rewrites in the four rewritten conditions. No code, prompt or configuration changed.
- Superseded: the earlier 24 October decision to train students on separate GPT-6.1 and Opus 5.5 datasets.
- Effect on existing runs: no trained run is affected, and the original-solution baseline stands. The GPT arm stays preserved as a screening record and will not be used for training.
- Open before generating the 100-question round: fix and record the Opus collection procedure (interface, displayed model, effort, shared versus per-question conversations). Decide whether the ten round-1 Opus responses are reused under that same procedure or regenerated. Human review of the flagged Opus candidates is still required before any training use. The multilingual-length and one-calculation exclusion observations above also still need decisions.

## 24 October 2026: complete meaning audit and Claude handoff

- The user requested a full meaning/wording audit with raw responses preserved and no human-review flags changed, then selected Opus for future research and asked for the results to be saved for a move to Claude. The teacher decision above remains authoritative; it does not approve examples or authorize training.
- The Codex AI audit read all 160 candidates against their source question and supplied solution. It identified three GPT-specific and five Opus-specific review items. The separate Claude review raised two additional candidates; those disagreements were carried forward. One ambiguous source question, `train-3341`, affects another sixteen variants. The combined queue has 26 unique candidates (12 GPT, 14 Opus).
- The other 134 have no specific flag in the combined queue, not human approval. All 160 remain `reviewed=false`. No semantic pass rate is claimed. This Codex audit was unblinded and occurred in the same conversation that generated GPT outputs; the external blind model verdicts were preserved, not replaced.
- Exact keys, raw-file lines, quotes and decisions needed: [meaning audit](pilots/2026-10-24-teacher-meaning-audit.md). The 160-candidate ledger, separate audit origins, source notes and user follow-up decision are in `artifacts/teacher-comparison/chat-export-round1/meaning-audit-20261024/audit.json`. `before.json` records 49 pre-existing input/raw/provenance/import/score file hashes; a separate hash identifies the external reviewer flags.
- [CLAUDE_HANDOFF.md](CLAUDE_HANDOFF.md) is the continuation entry point and results index. The local transfer bundle is `artifacts/handoff/2026-10-24-opus-teacher-results.zip`, containing the complete teacher phase (including Claude reproduction/review), prepared pilot data, relevant documentation/configuration and source. It excludes models, environments, caches, original-baseline adapters, personal recordings and unrelated output; ignored files still need a separate private backup.
- Raw responses, original provenance and prior score artifacts were preserved. No responses were repaired or regenerated, no review flag was set true, and no training, new teacher/student generation, condition selection, calibration tuning, official-test evaluation or public deployment ran during this audit/handoff. Existing work from the separate Claude session was preserved.

## 24 October 2026: train-3341 source interpretation accepted

- Question: whether the ambiguous source sentence in `train-3341` ("In the third week, 2000 more cases were recorded in the state.") keeps the question eligible. It can mean 2000 cases in week 3 or 2000 more than week 2.
- Decision (user, human): accept the supplied GSM8K interpretation, with 2000 cases in week 3 and a total of 9500. Keep the question and judge its candidates individually.
- Alternative considered: a matched exclusion from every condition. That would have required retraining the completed `pilot-original` baseline, which includes `train-3341` among its 100 training IDs.
- Effect: `train-3341` stays eligible in all five conditions. No gold answer, prompt, raw response, import, score or configuration changed, and no existing run needs rerunning. This approves no candidate. The 16 affected candidates (8 per arm) remain `reviewed=false` and still need individual human decisions.
- Record: decision `H-0001` in `artifacts/teacher-comparison/chat-export-round1/human-review-20261024/decisions.jsonl`. This file holds human decisions only, separate from raw responses and AI audits. It records the user's words, the source and raw-file hashes, and the Codex concern, and it keeps the per-candidate blind Sonnet/Opus verdicts.
- Later per-candidate human decisions (approve, reject or defer) are appended to that same ledger, starting with `H-0002`, in which the user approved OPUS-01 (`opus55/train-1258/multilingual/2`). The ledger is the authoritative per-candidate record. Each row keeps the exact raw line and its sha256 alongside the AI reviewers' views. Approval does not edit raw files or imports. A `reviewed=true` copy will be built only in a new directory, from approved rows, when the user asks.
- The user does not read Chinese. `H-0002` and `H-0003` were decided from the assistant's English glosses, so they are pending confirmation by a Mandarin-and-English reviewer (note `H-0004`). All 40 Opus multilingual candidates were compiled into a review worksheet for a bilingual teammate. It lists the source question, original solution, candidate steps, AI reviewer notes and an empty decision column. The worksheet is a private Google Doc in the user's Drive project folder, with a local copy and its sha256 in the same `human-review-20261024/` directory. The teammate's answers will be recorded in the ledger under the teammate's name. The English pool is not in the worksheet.

## 24 October 2026: instructor feedback on the proposal

- The user shared the instructor's written comments on the graded proposal. In paraphrase:
  1. The core experiments had no estimated time or cost range.
  2. The short-English baseline separates the benefit of shorter explanations from the benefit of mixing languages. Keep it central to the results.
  3. Use the planned repeated-scoring check to see whether two attempts per candidate give a stable enough ranking.
  4. Inspect what the trained model actually produces. Does it use both languages, and are the shorter solutions still complete? Examples where compression loses a necessary step would be worth discussing.
- Response to 1: [RESOURCE_ESTIMATE.md](RESOURCE_ESTIMATE.md), built from measured pilot rates. The milestone pilot needs about 12 to 15 GPU hours. The complete one-seed study needs about 174 to 252 GPU hours with the current runtime, two-thirds of it on the official test. Three seeds would need 440 to 645 hours, which does not fit the schedule unchanged. Opus teacher collection costs nothing extra through the subscription, or $43 to $126 at API list price ($21 to $63 batched). The estimate lists runtime and protocol options; none is adopted.
- Response to 2: no protocol change. `english-shortest` and `english-feedback` already exist. Report each multilingual condition first against its matched English condition, with the original-solution adapter as the ordinary fine-tuning reference. Screening suggests this comparison matters: multilingual Opus material was not shorter under the Qwen tokenizer (61.4 against 60.8 mean tokens).
- Response to 3: screening data motivates the check. With two attempts, feedback accuracy can only be 0, 0.5 or 1. The best accuracy was tied between candidates in 14 of 18 Opus pools. The feedback rule chose the same candidate as the shortest rule in 9 of 18 Opus pools (12 of 18 GPT). These are ten screening questions. If this persists, the feedback and shortest conditions differ on only part of the questions.
- Proposed check (not run, needs approval): on a fixed calibration subset, such as 50 questions, run `research score --split calibration --attempts 8` on a candidates file filtered to those IDs. No code change is needed. Seeds depend on question, pool, candidate and attempt, so attempts 0 and 1 reproduce the two-attempt score. Measure three things. First, how often picks from disjoint attempt pairs (0-1, 2-3, 4-5, 6-7) agree; these are independent repeats of the two-attempt rule. Second, how often each two-attempt pick matches the eight-attempt pick. Third, the share of questions where the feedback and shortest rules pick the same candidate. Fix the stability threshold and the fallback, such as more attempts, before looking at the results.
- Response to 4: target the proposal's 50-output inspection. Proposed per-output measures (not implemented): the share of Mandarin characters, and coverage of the gold intermediate results from GSM8K's `<<...>>` annotations. A correct output that skips an intermediate shows harmless compression. A wrong output missing an intermediate the solution needs is a candidate example of a lost step. These flags only choose what to read. A different valid calculation path produces different intermediates, so a human judges each sampled example. Compare the same question IDs across conditions.
- No code, configuration, prompt or run changed. The graded proposal was not edited.

## 10 November 2026: AI pre-review of the round-1 Mandarin worksheet

- The bilingual teammate had not started the round-1 Google Doc worksheet (40 Opus multilingual candidates); every decision cell was still empty. At the user's request, Claude Fable 5.2 (`claude-fable-5-2`, effort xhigh) reviewed all 40 against the worksheet's A/R/U rules, judging the Chinese text before reading the AI notes. Output: `ai-prereview-fable52-20261110.jsonl` in `artifacts/teacher-comparison/chat-export-round1/human-review-20261024/`, with an English gloss of every step.
- Result: 38 approve, 2 reject, 0 unsure. Rejected: `4833-M3` (`猴少5` and `狮多8` drop 比, so the ordinary reading reverses the direction) and `5032-M3` (`half phone 手机` names neither the charging nor the time). It agrees with the user's `H-0002` approval and `H-0003` rejection. It disagrees with both blind model checks on `4833-M3` and with the Sonnet flag on `1458-M3` (approved).
- This is a model judgment, not human review. It is not written to the human decision ledger. `H-0002` and `H-0003` still need a bilingual human's confirmation.

## 10 November 2026: decisions for the 100-question collection

- Decided by the user (human) in Claude Code chat, choosing among stated options:
  1. **Collection procedure:** Opus 5.5 rewrites for the remaining training questions are collected by fresh Claude Code subagents (Agent tool, model override `opus`), ten questions per subagent conversation, with the unchanged `teacher-comparison-v1` template. This matches round 1's ten-prompts-per-conversation pattern, so the ten round-1 responses are reused as training questions 1–10.
  2. **Calibration size:** the first 100 calibration questions, not 300. Enough for the penalty choice and the 50-question repeated-scoring check, at about a third of the scoring time. Supersedes the 300-question calibration in the proposal and `RESOURCE_ESTIMATE.md`.
  3. **One-calculation questions:** dropped from all five conditions, as `select` already does, because they cannot supply a feedback prefix. 11 of the 100 training questions have at most one annotated calculation (two have none). The matched original baseline is retrained on the retained IDs.
  4. **Review gate:** train an unreviewed screening series with `--allow-unreviewed` right away, while humans review only the selected rewrites. Then train a reviewed series before any official-test decision.
- Alternatives considered: one subagent per question (stricter isolation, but a different protocol from round 1), the user pasting prompts into claude.ai, 300 or 50 calibration questions, keeping one-calculation questions with a shortest-candidate fallback (needs a code change), and blocking training until review finishes.
- Not changed: the multilingual-length observation (not shorter under the Qwen tokenizer) needs no protocol change. It is reported by comparing each multilingual condition first with its matched English condition, as in the 24 October response to instructor feedback.

## 10 November 2026: Opus teacher collection for the pilot

- Prompt packs (no model calls): `scripts/prepare_teacher_comparison.py` gained `--split`, `--start`, `--count` and `--teachers`, with a test; the defaults reproduce the round-1 pack. Packs: `artifacts/teacher-collection/opus55-train-011-100-20261110/` (training positions 11–100) and `artifacts/teacher-collection/opus55-calibration-001-100-20261110/` (calibration positions 1–100). Template sha256 `b3f32c2b7bcc…` equals round 1.
- Instruction: [prompts/run-teacher-batch.md](../prompts/run-teacher-batch.md), filled per batch with ROOT, BATCH and QUESTIONS only. Nine training and ten calibration subagents ran on 10 November between about 19:15 and 19:25 +08:00. Each batch has `PROVENANCE-batch-NN.md` with the model label each subagent saw ("Opus 5.5", `claude-opus-5-5`), prompt and response hashes, and the session context it could see: the global CLAUDE.md and RTK.md, AGENTS.md and a "Ponytail" SubagentStart hook. Effort was unknown to most subagents; some saw a value of 40. Backend snapshot, seed, usage and cost are unknown.
- Failures: the first attempts at training batches 02 and 03 were stopped by a safety classifier before any response was written (zero files; questions are ordinary GSM8K arithmetic). Each was rerun once in a fresh subagent with the same instruction. `train-3562` and `train-618` have no `<<...>>` annotations in GSM8K, so a faithful rewrite has no steps; the subagents wrote `.FAILED.txt` records instead of inventing steps. Both questions are excluded from all conditions.
- Calibration import: `research rewrite --split calibration --limit 100 --import-file …/opus55/candidates.jsonl` into `artifacts/rewrites/opus55-pilot-calibration-20261110/`. 800 candidates, 792 pass. The 8 failures are all of `train-394`, whose source annotation `560//10=56` uses floor division, which the validator rejects; that question is unusable for calibration.
- Training import: round-1 raw responses for questions 1-10 (verified byte-identical rows to the round-1 import) plus the new batches, consolidated in training order into `opus55/candidates-pilot-train-1-100.jsonl` in the training pack, then `research rewrite --split train --import-file ...` into `artifacts/rewrites/opus55-pilot-train-20261110/`. 784 candidates for 98 questions; all 784 pass arithmetic/structure checks; all `reviewed=false`. Static prefix check: 89 questions have feedback-eligible candidates; the other 9 (`train-35`, `train-654`, `train-2078`, `train-2158`, `train-3205`, `train-3620`, `train-4207`, `train-4267`, `train-6644`) have one annotated calculation and will be excluded with `train-3562` and `train-618`, leaving at most 89 matched IDs.
- Subagents noted source quirks (unannotated calculations carried in step text, GSM8K typos such as "bracelets" for necklaces, and a few source solutions that answer a different reading of the question). These are listed per batch in the provenance files for the human reviewers. No response was edited, repaired or regenerated; every `reviewed` flag is false.
- Limitation: questions 1–10 came from the main repository conversation on 24 October (with chat-style hooks in context), and questions 11–100 from subagents with a smaller context. Both used one conversation for ten prompts and the same template.
- Code: `core.select_conditions` now skips candidates marked `"human_rejected": true` while keeping the pool complete, so a reviewer's rejection substitutes the next-best candidate instead of removing the question. A test was added; the full suite passes.
- Handoff: the user will run the GPU pipeline in Codex with [prompts/codex-pilot-pipeline.md](../prompts/codex-pilot-pipeline.md). It fixes the stability rule and penalty rule before any results are seen. No scoring, selection, training, evaluation or official-test work ran in this session.

## Copy for a research decision

```text
Date and researchers:
Question being decided:
Evidence / calibration or development run IDs:
Decision and reason:
Alternatives considered:
Configuration or protocol fields changed:
Previous decision superseded, if any:
Effect on existing runs and which comparisons need rerunning:
```

## Copy for a run or teammate handoff

```text
Date, researcher and run ID:
Purpose (smoke / screening / pilot / final):
Git commit and clean/dirty status; source snapshot if dirty:
Exact command from the repository root:
Config file and seed:
Prepared-data manifest, model revision and dataset revision:
Teacher version / prompt provenance, if relevant:
Inputs and artifact archive location (no credentials):
Outputs / adapter / predictions / summary location:
Hardware and relevant power/thermal settings:
Elapsed time, peak memory, teacher/GPU cost where applicable:
Observed result and failed/truncated/unparseable counts:
Human review performed, by whom, and remaining limitations:
Next action and owner:
```
