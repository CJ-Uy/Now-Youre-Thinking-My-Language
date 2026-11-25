# Codex instruction: run the Opus 5.5 pilot pipeline (10 November 2026)

Paste the block below into Codex (ChatGPT's coding agent) opened at this repository's root on the GPU laptop. It takes over from the Claude session that collected the Opus teacher data. Claude produced teacher data only; this instruction covers scoring, calibration, selection, training, evaluation, review worksheets and documentation.

```text
You are continuing the COMP 4901B compact multilingual reasoning study in this repository. You drive the GPU pipeline from teacher data to development results. Work carefully: research integrity matters more than speed.

## Read first
AGENTS.md, README.md, docs/TEAM_GUIDE.md, docs/EXPERIMENT_LOG.md (especially the 10 November 2026 entries), docs/CLAUDE_HANDOFF.md, docs/RESOURCE_ESTIMATE.md and prompts/run-teacher-batch.md. Follow AGENTS.md exactly. In particular: preserve earlier results, use new output directories, keep all five matched conditions, keep failures/truncations, never open the official test without the user's explicit opt-in, and record every run and decision in docs/EXPERIMENT_LOG.md.

## Current state (verified by the Claude session on 10 November 2026)
- Student: Qwen3-0.6B, thinking disabled. Teacher: Opus 5.5 (decided 24 October). Data lock: configs/pilot-data-lock.json.
- Training-split teacher candidates for all 100 pilot training questions: artifacts/rewrites/opus55-pilot-train-20261110/candidates.jsonl (imported with `research rewrite --split train`). Questions 1-10 reuse the round-1 screening responses; questions 11-100 come from artifacts/teacher-collection/opus55-train-011-100-20261110/. Two questions (train-3562, train-618) have no <<...>> calculations in GSM8K, so the teacher could not rewrite them; they are absent from the candidate file and select excludes them from all five conditions.
- Calibration candidates for the first 100 calibration questions: artifacts/rewrites/opus55-pilot-calibration-20261110/candidates.jsonl (imported with `research rewrite --split calibration --limit 100`).
- Every candidate has reviewed=false. Nothing is human-approved yet.
- User decisions recorded on 10 November: (1) collection procedure above; (2) calibration uses the first 100 calibration questions, not 300; (3) one-calculation and zero-calculation questions are dropped from all five conditions (current select behaviour; about 11 of 100); (4) train an UNREVIEWED SCREENING series now with --allow-unreviewed while humans review the selected rewrites in parallel, then train a REVIEWED series before any official-test decision.
- Code change already made and tested: research/core.py select_conditions skips candidates with "human_rejected": true while keeping the pool complete.
- Human decisions ledger (append-only, authoritative): artifacts/teacher-comparison/chat-export-round1/human-review-20261024/decisions.jsonl (H-0001 to H-0004 exist). H-0002 approve and H-0003 reject were made by CJ from English glosses and still need a bilingual reviewer's confirmation. An AI pre-review (Claude Fable 5.2, not a human review) of the 40 round-1 multilingual candidates is in ai-prereview-fable52-20261110.jsonl in that same directory.

## Rules for this run
- One GPU job at a time. Laptop on AC power with the same performance mode for every timed run; log it.
- Use a single copied config for the whole series: copy configs/pilot.json to configs/pilot-opus55.json, set length_penalty to the calibrated value (step 3), and pass --config configs/pilot-opus55.json BEFORE the subcommand for every command from step 4 onward, including the unchanged-model evaluation, so every compared run shares one config hash. Do not edit configs/pilot.json.
- Run the unit tests (.venv/Scripts/python.exe -m unittest discover -s tests -v) and `research doctor` first, and after any code change. Add a test for any nontrivial code you write.
- Do not commit or push unless the user asks; pushing main deploys the public site. Never put artifacts/ content in explainer/public/.
- Label every unreviewed run "screening" in its directory name and log entry. Screening results establish nothing final.
- After each phase, zip the new artifact directories into artifacts/handoff/ and remind the user to back them up privately; Git does not carry artifacts/.

## Step 0: preflight
Verify the data lock (README command), the candidate files' line counts (train: 784 rows for 98 questions, all passing validation; calibration: 800 rows, of which the 8 train-394 rows fail validation because the source uses //), unique (id, pool, candidate) keys, all reviewed=false, and that both import manifests exist. About 89 training questions are feedback-eligible, so expect at most 89 matched IDs after select. Report and stop if anything differs.

## Step 1: calibration scoring (about 2 GPU hours)
research score --split calibration --candidates artifacts/rewrites/opus55-pilot-calibration-20261110/candidates.jsonl --output artifacts/scores/opus55-calibration-a2-20261110

## Step 2: repeated-scoring stability check (about 4 GPU hours; instructor feedback point 3)
Before running it, append to the experiment log the pre-registered rule below, unchanged:
"Stability rule (adopted by the user via the Codex instruction of 10 November 2026): on the first 50 calibration questions, score every candidate with 8 attempts. Attempts 0-1 must reproduce step 1 exactly. Measure (a) agreement of the feedback-rule pick across the disjoint attempt pairs 0-1, 2-3, 4-5, 6-7; (b) the share of eligible pools where the two-attempt pick equals the eight-attempt pick; (c) the share where the feedback pick equals the shortest pick. If (b) is below 0.60, training candidates are scored with 4 attempts instead of 2; otherwise with 2."
Then filter the calibration candidates to the first 50 calibration question IDs (order of artifacts/data/pilot/calibration.jsonl) into a new file and run:
research score --split calibration --attempts 8 --candidates <filtered file> --output artifacts/scores/opus55-calibration-first50-a8-20261110
Compute (a)-(c) with a small script under scripts/ (with a test), save JSON next to the scores, and log the results and which attempt count applies.

## Step 3: length-penalty calibration (CPU)
Before computing, append this pre-registered rule to the log, unchanged:
"Penalty rule (adopted by the user via the Codex instruction of 10 November 2026): on the step-1 calibration scores, apply core.select_conditions for penalties 0, 0.05, 0.1, 0.2, 0.3, 0.5 and 1.0. For each pool, compute the mean feedback accuracy and mean student-tokenizer tokens of the feedback-rule picks. Choose the largest penalty whose mean pick accuracy is at least the penalty-0 value minus 0.05 in both pools. Report the token reduction against penalty 0."
`research select` refuses calibration scores, so call core.select_conditions directly from a small script (with a test). Save the table, write configs/pilot-opus55.json with the chosen penalty, and log the decision with the evidence path.

## Step 4: training-candidate scoring (about 2 GPU hours, 4 if step 2 requires 4 attempts)
research --config configs/pilot-opus55.json score --candidates artifacts/rewrites/opus55-pilot-train-20261110/candidates.jsonl [--attempts 4 only if step 2 says so] --output artifacts/scores/opus55-train-20261110

## Step 5: selection (screening)
research --config configs/pilot-opus55.json select --scored artifacts/scores/opus55-train-20261110/scored.jsonl --output artifacts/conditions/opus55-screening-20261110
Report retained and excluded IDs with reasons. Expected exclusions: the one-calculation questions, plus anything without a valid candidate in a pool.

## Step 6: human review worksheets (CPU; start right after step 5, before training)
Build two worksheets from the unique picks across the four rewritten conditions:
- artifacts/human-review/pilot-20261110/english-review-sheet.html for CJ (English pool picks).
- artifacts/human-review/pilot-20261110/mandarin-review-sheet.html for the bilingual reviewer (multilingual pool picks).
Copy the layout, instructions and A/R/U rules of artifacts/teacher-comparison/chat-export-round1/human-review-20261024/mandarin-review-sheet.html: per question the question text, original solution, then one row per pick with steps as "text [equation]", a notes column and an empty decision column. Label picks by question and candidate key (for example 4833-M3 or 4833-E1). In the notes column show, where available: the Fable pre-review verdict and reason (round-1 multilingual only) and any earlier ledger decision marked "needs confirmation". You may add your own AI reading, clearly labelled "GPT AI hint, may be wrong"; never present it as a review. Put "check these first" items at the top. Save sha256 hashes in a manifest beside the sheets. The user will upload the HTML to Google Drive and open it with Google Docs; if a Google Drive connector is available in this session, you may instead create private Google Docs in the user's research folder after asking. Never share the docs or include personal data.

## Step 7: screening training and quick development check (about 2.5 GPU hours)
Train the five conditions from artifacts/conditions/opus55-screening-20261110 with --allow-unreviewed into artifacts/runs/opus55-screening-<condition>. Then evaluate the unchanged model and the five adapters on the first 50 development questions at budget 256 (--limit 50 --budget 256), all with configs/pilot-opus55.json. Compare with `research compare`: each multilingual condition against its matched English condition first, then each rewritten condition against the matched original adapter, and the original adapter against the unchanged model. Write docs/pilots/2026-11-10-opus55-screening.md with the table, failures, truncations, unparseable counts, the tokenizer observation that multilingual material was not shorter in screening, and clear SCREENING labels.

## Step 8: record human reviews (repeat as answers arrive)
Already recorded on 20 November (do not re-append): H-0005 to H-0044 (bilingual review of the 40 round-1 multilingual candidates) and H-0045 (exclude train-2867 from all five conditions because its GSM8K answer looks wrong). In the review Doc, decision cells that say "ALREADY DONE in round-1 Doc" or "REMOVED from the study" are notes, not new decisions; read the ledger for those rows. When building the reviewed scored copy, set human_rejected=true on every train-2867 candidate so select removes that question from every condition (see docs/DATASET_NOTES.md). AI pre-reviews in artifacts/human-review/pilot-20261110/ai-prereview-*-fable52-20261120.jsonl are hints only and never count as decisions.
When the user gives you reviewer answers, append one ledger row per decision (next H-number) with reviewer name exactly as the user gives it, decision, reason, candidate key and raw-line sha256, following the existing ledger rows' fields. Never infer a decision. Then build, in a NEW directory, a copy of the training scored.jsonl where approved picks have reviewed=true and rejected candidates have human_rejected=true, re-run select into a new conditions directory, and make a short worksheet of only the new replacement picks. Loop until every pick in all four rewritten conditions is approved. Picks that are never reviewed stay reviewed=false.

## Step 9: reviewed series (about 1 GPU day)
When every pick is approved, train the five conditions WITHOUT --allow-unreviewed into artifacts/runs/opus55-reviewed-<condition>. Run the full development sweep (all 200 development questions at budgets 128, 256 and 512) for the unchanged model and the five adapters. Compare as in step 7. Then review and test scripts/inspect_outputs.py (an untested draft from 24 October; read it fully, add a small test, fix only real bugs) and use it to choose 50 development outputs per condition for human reading (instructor feedback point 4). Write docs/pilots/<date>-opus55-reviewed.md.

## Step 10: STOP before the official test
Do not run `freeze` or the official test on your own. Present the options with GPU-hour estimates from docs/RESOURCE_ESTIMATE.md (all three budgets for six models is 111-167 hours; one budget chosen on development data is about a third). Wait for the user's explicit choice, log it, then run `freeze` and the official test with --final-test and --frozen-settings exactly as in the README.

## Reporting
At every stop, tell the user: what ran (commands), what was verified, what failed or remains untested, where outputs are, elapsed GPU time, and the next action. Update docs/TEAM_GUIDE.md status and docs/EXPERIMENT_LOG.md as you go. Be explicit about anything you could not verify.
```
