# Team guide and project context

This guide preserves the context needed to join the project without the original chat. Start with the root [README](../README.md) for installation and commands.

## What we are testing

Can a small language model learn to solve arithmetic word problems with fewer generated tokens by training on compact written solutions? In particular, does allowing English–Mandarin mixing help beyond compact English and equations, and does student feedback select better examples than brevity alone?

We are adapting an existing model with LoRA, not training a language model from scratch. The research concerns observable written solutions and answer accuracy. It cannot establish the model's internal reasoning process.

| Term | Meaning here |
|---|---|
| Student | The small model being trained and evaluated |
| Teacher | A stronger model proposing rewritten versions of supplied solutions |
| Token | A unit produced by the student's tokenizer; it is not necessarily a word |
| LoRA / adapter | Small trainable additions to a model whose original weights stay frozen |
| Calibration | Separate examples used to choose candidate-selection settings |
| Development | Separate examples used to choose training/evaluation settings |
| Official test | Held-out examples used only after decisions are fixed |
| Reasoning budget | Maximum generated tokens allowed for the visible calculation steps |

The current study is in [final-project-proposal.md](../final-project-proposal.md). The older meeting brief and `research-proposal.md` contain superseded counts and baseline arrangements. Use the final proposal and explicitly logged later decisions when they differ. The repository's COMP4601B directory name differs from the COMP 4901B course named in the final proposal.

## Controlled comparison

| Condition ID | Training solutions | Selection |
|---|---|---|
| `original` | Unchanged GSM8K English solutions | Original supplied solution |
| `english-shortest` | English and equations | Shortest valid candidate |
| `english-feedback` | English and equations | Frozen student accuracy minus token penalty |
| `multilingual-shortest` | English, Mandarin and equations allowed | Shortest valid candidate |
| `multilingual-feedback` | English, Mandarin and equations allowed | Frozen student accuracy minus token penalty |

The unchanged pretrained student is an additional reference, not a sixth training condition. All five trained conditions must share the base checkpoint, original question IDs, training settings and evaluation settings. If a question is excluded during candidate preparation, it must be excluded from the matched original baseline too.

The multilingual-feedback versus English-feedback comparison tests access to language mixing. The multilingual-feedback versus multilingual-shortest comparison tests feedback selection. The original-solution adapter checks whether rewriting helps beyond ordinary fine-tuning. A finding that concise English works just as well is a valid negative result.

## Starting settings and data

- Student: Qwen3-0.6B initially. A Qwen3-1.7B feasibility comparison is planned before fixing the final model.
- Task: GSM8K, with 7,473 official training questions and 1,319 official test questions.
- Pilot: 100 training questions, separate 300 calibration and 200 development questions, selected from the official training pool using seed 42.
- Later scale: provisionally 1,000 training questions including the pilot. Prepare a new data directory and regenerate all conditions together when expanding.
- Candidate pools: four English/equation and four multilingual/equation rewrites per question. Teacher: **Opus 5.5**, chosen on 24 October 2026 after a ten-question GPT-6.1 versus Opus 5.5 screening round ([protocol](TEACHER_COMPARISON.md), [results](pilots/2026-10-24-teacher-screening.md)). The teacher-specific student comparison was dropped; GPT outputs are kept only as a screening record.
- Feedback: first half of the candidate's steps, no final answer, two student completions initially; recheck a subset with eight.
- Training: LoRA, initially batch size 1 and accumulation 8. Maximum sequence length, epochs and other defaults are in `configs/pilot.json` and remain provisional until profiled.
- Evaluation: question alone; reasoning budgets 128, 256 and 512, followed by up to 64 answer tokens. Report accuracy, generated tokens, elapsed time, failures and truncations together.
- Proposed target: 20% fewer tokens with at most a three-percentage-point accuracy loss against the relevant baseline. This is a target, not a result.

Calibration chooses candidate-selection settings. Development chooses training/evaluation settings. Neither updates model weights. The official test set is reserved for final evaluation after decisions are frozen. The fresh 200-question transfer set needs independent held-out templates and known answers; it has not been designed by setup.

## What exists and what remains

**Course GPU pilot, 21 November 2026 (+08:00).** All six models completed all 200 development questions at each of budgets 128, 256 and 512 on the same RTX 2080 Ti. The 3,600 predictions and all 21 paired comparisons are verified. The private worksheet contains 48 outputs for human reading. [Course GPU pilot report](pilots/2026-11-21-opus55-aiassist-school.md)

**Laptop pilot, 20–21 November 2026 (+08:00).** Five adapters trained on the same 86 question IDs. All six quick development checks finished. The unchanged model and the original-solution adapter each completed a full laptop evaluation before the owner closed the laptop queue. In each multilingual condition, 10 selections had recorded human approval and 76 had only Fable's approval under H-0046. Those 76 retain `reviewed=false`. Both AI-assisted, unreviewed series use the same single training seed and are ineligible for official testing. [Laptop pilot report](pilots/2026-11-20-opus55-aiassist.md)

**School screening as of 11 November 2026 (+08:00):** school Steps 1–7 finished at 00:46 on `ughost03`; Step 8 is waiting for human decisions. Calibration selected length penalty 1.0 and two attempts. Five matched screening adapters use 88 question IDs; all six 50-question development evaluations are complete. See the [unreviewed screening report](pilots/2026-11-10-opus55-screening.md). These results do not establish a final language-mixing benefit, and official testing remains unopened.

The new human-review Google Doc (link shared with the team directly and kept out of this public repository) contains separate **Mandarin — teammate** (111 rewrites) and **English — CJ** (110 rewrites) tabs, each covering 88 questions. The complete source text was verified after transfer; AI hints remain labeled and all decisions are blank. It is private in the owner's My Drive until the owner grants teammate access. Reviewers should fill names/dates and A/R/U decisions, with reasons for R/U. Do not infer approval from AI notes or the screening run. All 18 phase archives have verified local copies, including every adapter and prediction set. Earlier dated entries below describe the setup and launch history.

The repository contains the proposal, explainer website, Python pipeline, pilot config, local setup script, tests and reproduction instructions. The code supports preparing splits, importing/generating rewrites, validating calculations, scoring partial solutions, creating matched conditions, training adapters and evaluating runs.

Environment setup and small GPU smoke checks verify that software can run. The full 100-question original-solution adapter has subsequently completed three training epochs. The user selected a quick evaluation on 50 development questions at reasoning budget 256; see the [pilot report](pilots/2026-10-24-original-baseline.md) for status and measurements. The full 200-question, three-budget sweep is deferred. Check `docs/SETUP_VERIFICATION.md` for setup checks; use the experiment log for subsequent runs.

Research work still required:

**Status on 10 November 2026:** Opus 5.5 teacher candidates now exist for 98 of the 100 pilot training questions and the first 100 calibration questions; nothing is human-reviewed or scored yet. The user chose to hand the GPU pipeline to Codex with [prompts/codex-pilot-pipeline.md](../prompts/codex-pilot-pipeline.md): calibration and stability scoring, penalty choice, selection, an unreviewed screening series, human review worksheets for the selected rewrites, then a reviewed series. See the 10 November entries in the [experiment log](EXPERIMENT_LOG.md).

**Codex preflight, 10 November 2026, 19:32 +08:00:** the locked splits, import manifests, candidate counts, unique keys, review flags and expected validation failures pass; all 33 Python tests pass and CUDA is available. Static feedback checks allow at most **88 matched training IDs**: in addition to the eleven zero/one-calculation questions, `train-3938` has no eligible multilingual prefix under the existing final-answer leakage rule. Step 1 has not started because another Python GPU job is running; the one-GPU-job rule requires resolving that conflict first. Evidence: `artifacts/preflight/opus55-pilot-20261110-1931/`. No research code, pilot config or candidate data changed. See the experiment log for the stop and next command.

**School setup, 10 November 2026:** at the user's request, the project is now installed privately at `/store/cjuy/comp4901b-pilot-20261110/repo`, on the same `opus55-pilot-pipeline` branch. Verified on `ughost03` (RTX 2080 Ti): all 33 tests, locked data, pinned environment and serial inference/training/adapter smoke checks pass. The unchanged runtime selects emulated BF16 on this GPU. See [SCHOOL_GPU.md](SCHOOL_GPU.md) for reconnection, evidence and limitations. The pilot remains paused before Step 1; no calibration score or research-series adapter has been produced. Idle compute access is released after setup and backup.

For the move to Claude, use [CLAUDE_HANDOFF.md](CLAUDE_HANDOFF.md) as the results index and current scope. The combined [meaning-review queue](pilots/2026-10-24-teacher-meaning-audit.md) lists 26 priority candidates from both AI audits; every candidate still has `reviewed=false`. Teacher selection does not authorize training or approve those candidates.

The [time and cost estimate](RESOURCE_ESTIMATE.md) gives GPU-hour, teacher-cost and review-time ranges for each stage, built from measured pilot rates. Evaluation, not training, dominates.

1. Profile the pilot and compare the two proposed student sizes before fixing one.
2. Teacher chosen: Opus 5.5 (see the experiment log). Fix the Opus collection procedure for the 100-question round and human-review the flagged round-1 candidates. Screening history: review the matched GPT-6.1 and Opus 5.5 outputs for preserved meaning. Both teachers have 80/80 mechanically valid candidates, and common feedback scoring is complete: 83/144 strict-format successes for GPT and 86/144 for Opus, with wide uncertainty. All candidates remain unreviewed, including a preserved GPT wording flag; no teacher winner or downstream training result is established. See the [screening comparison](pilots/2026-10-24-teacher-screening.md) and keep the original model/mode, prompts, raw outputs and available usage data.
3. Generate candidate rewrites, inspect arithmetic-validation failures and review meaning. Both researchers should inspect a sample; any change in meaning disqualifies that rewrite.
4. Calibrate the length penalty and assess feedback ranking stability.
5. Complete the matched five-condition training/evaluation and repeat seeds if resources permit.
6. Build the independent transfer set, inspect 50 outputs, document limitations and write the report.

Do not interpret the default length penalty `0.1`, model choice, data sizes or training recipe as an empirically chosen optimum. Reinforcement learning/GRPO is an optional extension after the core comparison and has not been implemented.

## How a teammate reproduces a run

1. Check out the same Git commit. If the run says `git_dirty: true`, obtain the exact source snapshot or patch as well; the commit alone is insufficient.
2. Install Python 3.12 and a compatible NVIDIA driver. Run `scripts/setup.ps1`, `doctor`, the Python tests and the website checks as described in the README. `requirements-lock.txt` pins the complete tested environment.
3. Use the same config and immutable model/dataset revisions. `prepare` can reconstruct splits from those revisions, sizes and seed. The run manifest lists actual IDs and file hashes; verify these before comparing results. The committed `configs/pilot-data-lock.json` records the setup pilot's exact identity; the README includes its verification command. Machine metadata and timestamps can differ without changing the dataset identity.
4. Obtain the experiment's ignored artifact archive separately. Preserve its directory structure, especially the prepared-data manifest, teacher prompts/raw outputs, scored candidates, selected condition files, adapter metadata and predictions. Do not expect Git clone to supply model weights or experiment results.
5. Run the same command, seed, adapter and token budget into a new output directory. Log GPU model, power/thermal conditions, elapsed time and failures. Exact GPU sampling and timing may vary across hardware/software even when settings match.
6. Use `compare` for paired runs with identical question IDs and evaluation settings. Inspect the raw failures as well as averages. A confidence interval over questions does not substitute for multiple training seeds.

The code's saved manifests are the source of truth for an executed run. A prose setting in an old document does not override them. If protocol changes are needed, record a decision and create a new run series; preserve the old results.

## Team handoff and work split

The proposal suggests one researcher leads data preparation/language review and the other leads feedback selection/training/compute profiling. Confirm names and assignments together; no teammate identity or task acceptance is assumed here. Both review failure cases and check each other's work.

For each handoff, add an entry to [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md) containing the command, source revision, config, input IDs/artifact archive location, output location, measured outcome, known limitations and next action. Put decisions there before updating the proposal or public progress page.

The proposal's dates are 29 October 2026 for the milestone, 24–26 November for presentations and 4 December for the report. Confirm course announcements if these change. The milestone aims for a complete 100-problem pipeline and original-solution baseline, with multilingual selection and resource profiling checked.

## Access and sharing

No hosted-model API key is required for the original baseline. Rewriting needs a chosen teacher: import outputs from a model you already have access to, or install/run the local Ollama fallback described in the README. Paid teacher usage and additional GPU rental need an agreed team budget.

Share private experiment artifacts through an agreed team storage location. Record the location in the log without passwords or tokens. Only explicitly reviewed result evidence belongs under `explainer/public/`; raw recordings, private data and local credentials do not.

**School continuation authorized, 10 November 2026:** Step 1 is running on `ughost03`. The tested one-shot queue continues through Steps 2–7, then stops for human review. Current remote state: `artifacts/pipeline/opus55-school-screening-20261110/status.json`. Remote documentation receives phase updates; pull it before editing locally. See `docs/SCHOOL_GPU.md`.

- Launch verified at 20:30 +08:00: Step 1 worker PID 13631 and continuation PID 14096 are detached and running on ughost03. All 43 tests and doctor pass on the school environment. At 20:29:57, 407/1478 Step 1 attempts were saved (0 runtime errors, 1 truncation, 69 unparseable answers); all are retained. Mean generation time 2.3834 s gives 3.6-4.5 remaining scoring hours, depending on the stability rule; allow additional training/evaluation/archive time. Planning finish window: 02:00-05:00 on 11 November +08:00; check at 08:00. This is an estimate, not a completion promise.
- The detached jobs survived a brief SSH disconnect and were verified under the same PIDs after reconnection. The compute login now runs an explicit bash wait for queue.done and exits when the queue terminates. Queue completion or failure is determined by status.json, not SSH-window presence.

- GPU-utilization decision, 10 November: user chose to keep the active school pipeline unchanged after reviewing batching/reproducibility tradeoffs. Performance benchmarking is deferred; current queue continues. See experiment log.

- School pipeline 2026-11-10T13:12:48.446514+00:00: Step 1 completed: {"candidates": 800, "attempts": 1478, "errors": 0, "truncated": 1, "unparseable": 309, "generation_seconds": 3518.6192623050156}. Outputs: `artifacts/scores/opus55-calibration-a2-20261110`.

- School pipeline 2026-11-10T13:12:48.569331+00:00: Phase step1 archived at `artifacts/handoff/2026-11-10-opus55-school-step1.zip` (SHA-256 `e89b83365ae96566394fbf3f3e2487269e2880ecba114e60d4331aed14e7798a`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T15:12:45.725795+00:00: Step 2 completed: {"eligible_pools": 96, "penalty_for_stability": 0.1, "reproduction": "All recorded attempt fields match except elapsed seconds", "pairwise_agreement": 0.6006944444444444, "all_four_pairs_agree": 0.3854166666666667, "two_equals_eight": 0.6458333333333334, "two_equals_shortest": 0.5833333333333334, "eight_equals_shortest": 0.4375, "each_pair_equals_shortest": [0.5833333333333334, 0.59375, 0.59375, 0.6145833333333334], "training_attempts": 2}. Evidence: `artifacts/scores/opus55-calibration-first50-a8-20261110`.

- School pipeline 2026-11-10T15:12:45.871949+00:00: Phase step2 archived at `artifacts/handoff/2026-11-10-opus55-school-step2.zip` (SHA-256 `8c6dfbdda1ea01931c4affc23624772a313c298b435b4b5b66ec9582b4d03b7d`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T15:12:52.836164+00:00: Step 3 chose length_penalty=1.0; config `configs/pilot-opus55.json` SHA-256 `4c2cce25f583d483688ba9013809c054509a8cfcfb9e3fe15d6e32fb9a305604`. Full table and token reductions: `artifacts/scores/opus55-calibration-a2-20261110/penalty.json`.

- School pipeline 2026-11-10T15:12:52.902492+00:00: Phase step3 archived at `artifacts/handoff/2026-11-10-opus55-school-step3.zip` (SHA-256 `c2797868bac0f801f8333e1889f9ba65e1b5227702e4518b2f88d025363ced74`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T16:07:59.823515+00:00: Step 4 completed: {"candidates": 784, "attempts": 1396, "errors": 0, "truncated": 1, "unparseable": 243, "generation_seconds": 3294.113026735009}. Evidence: `artifacts/scores/opus55-train-20261110`.

- School pipeline 2026-11-10T16:07:59.944149+00:00: Phase step4 archived at `artifacts/handoff/2026-11-10-opus55-school-step4.zip` (SHA-256 `44d216c996b1170160e6da8699603e9efeb1700c5a1a0b63d7f327ffd043c59d`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T16:08:03.445958+00:00: Step 5 retained 88 identical IDs: ['train-1458', 'train-6312', 'train-4833', 'train-5032', 'train-1914', 'train-1258', 'train-5173', 'train-3457', 'train-3341', 'train-1740', 'train-1770', 'train-6698', 'train-7373', 'train-5862', 'train-3248', 'train-5189', 'train-4307', 'train-4225', 'train-3103', 'train-4439', 'train-4700', 'train-862', 'train-6453', 'train-3161', 'train-7162', 'train-1660', 'train-3753', 'train-3940', 'train-7348', 'train-7224', 'train-6562', 'train-4779', 'train-4355', 'train-3797', 'train-6372', 'train-333', 'train-3718', 'train-5160', 'train-4210', 'train-5822', 'train-5236', 'train-3050', 'train-2505', 'train-1084', 'train-2867', 'train-6425', 'train-1197', 'train-5459', 'train-7129', 'train-5525', 'train-3139', 'train-6487', 'train-4185', 'train-623', 'train-3650', 'train-1890', 'train-995', 'train-4669', 'train-7315', 'train-1456', 'train-2427', 'train-2368', 'train-7202', 'train-6710', 'train-852', 'train-2891', 'train-2616', 'train-7287', 'train-6394', 'train-2698', 'train-6456', 'train-224', 'train-3101', 'train-7439', 'train-3751', 'train-37', 'train-6419', 'train-7186', 'train-1662', 'train-963', 'train-2930', 'train-2257', 'train-1226', 'train-2448', 'train-1578', 'train-2621', 'train-4575', 'train-7425']. Exclusion reasons: `artifacts/conditions/opus55-screening-20261110/selection-audit.json`.

- School pipeline 2026-11-10T16:08:03.548271+00:00: Phase step5 archived at `artifacts/handoff/2026-11-10-opus55-school-step5.zip` (SHA-256 `32e0b54d4acf1456ed511c7d4e0d8d8b8097464c54002e5eafa92640fc9e2855`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T16:08:03.576703+00:00: Step 6 review sheets ready: `artifacts/human-review/pilot-20261110`; unique picks: {"english": 110, "multilingual": 111}. No human approval was inferred.

- School pipeline 2026-11-10T16:08:03.699753+00:00: Phase step6 archived at `artifacts/handoff/2026-11-10-opus55-school-step6.zip` (SHA-256 `a352a39cfc5f162e671d26be91204f6a28308facd9c376c21918a77a2b59e92d`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T16:10:12.200974+00:00: Step 7 train-original complete: `artifacts/runs/opus55-screening-original`.

- School pipeline 2026-11-10T16:10:16.636767+00:00: Phase train-original archived at `artifacts/handoff/2026-11-10-opus55-school-train-original.zip` (SHA-256 `0395b4442680544938c9861b906b0abf57a948867398ba7e83892720dd13a5f2`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T16:12:26.185536+00:00: Step 7 train-english-shortest complete: `artifacts/runs/opus55-screening-english-shortest`.

- School pipeline 2026-11-10T16:12:30.649929+00:00: Phase train-english-shortest archived at `artifacts/handoff/2026-11-10-opus55-school-train-english-shortest.zip` (SHA-256 `040138cdb75e1428bb92330a37253add113549d18d884f42264796e116393080`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T16:14:40.529300+00:00: Step 7 train-english-feedback complete: `artifacts/runs/opus55-screening-english-feedback`.

- School pipeline 2026-11-10T16:14:44.966631+00:00: Phase train-english-feedback archived at `artifacts/handoff/2026-11-10-opus55-school-train-english-feedback.zip` (SHA-256 `4d01dd4b9a6a69c464da0b4aed46a17dbca08dbfd2f1167826cd687fbc963dd1`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T16:16:51.402753+00:00: Step 7 train-multilingual-shortest complete: `artifacts/runs/opus55-screening-multilingual-shortest`.

- School pipeline 2026-11-10T16:16:55.863843+00:00: Phase train-multilingual-shortest archived at `artifacts/handoff/2026-11-10-opus55-school-train-multilingual-shortest.zip` (SHA-256 `9278f3c762fec8b7033f8482c0e9147666076abe484851f270f20244620a6801`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T16:19:03.746980+00:00: Step 7 train-multilingual-feedback complete: `artifacts/runs/opus55-screening-multilingual-feedback`.

- School pipeline 2026-11-10T16:19:08.219716+00:00: Phase train-multilingual-feedback archived at `artifacts/handoff/2026-11-10-opus55-school-train-multilingual-feedback.zip` (SHA-256 `3f1679f6b4ee37bc1aaef2494bd9bb62be17c2047ab7db79bc3071d4c9bdba00`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T16:24:09.784124+00:00: Step 7 eval-unchanged complete: `artifacts/runs/opus55-screening-unchanged-eval`.

- School pipeline 2026-11-10T16:24:09.900978+00:00: Phase eval-unchanged archived at `artifacts/handoff/2026-11-10-opus55-school-eval-unchanged.zip` (SHA-256 `2f4a39345193e5cdd885105b3e16927f4fbb396bc06cdae695f33ada598d9d4d`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T16:31:10.397855+00:00: Step 7 eval-original complete: `artifacts/runs/opus55-screening-original-eval`.

- School pipeline 2026-11-10T16:31:10.516251+00:00: Phase eval-original archived at `artifacts/handoff/2026-11-10-opus55-school-eval-original.zip` (SHA-256 `712a0637e0549b187f801543dd22a24df06889541a698310b29b03c6fd643d69`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T16:35:09.867544+00:00: Step 7 eval-english-shortest complete: `artifacts/runs/opus55-screening-english-shortest-eval`.

- School pipeline 2026-11-10T16:35:09.984096+00:00: Phase eval-english-shortest archived at `artifacts/handoff/2026-11-10-opus55-school-eval-english-shortest.zip` (SHA-256 `7f4392361160fcf2a3c72b5f561ff45fe8051a81dff78c93c9683b7a961d29b6`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T16:39:01.117213+00:00: Step 7 eval-english-feedback complete: `artifacts/runs/opus55-screening-english-feedback-eval`.

- School pipeline 2026-11-10T16:39:01.235286+00:00: Phase eval-english-feedback archived at `artifacts/handoff/2026-11-10-opus55-school-eval-english-feedback.zip` (SHA-256 `c9e8be544869269dd2f7b54b034febeed25716d95a72dc9edf15f6f7d96e2e21`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T16:42:49.262714+00:00: Step 7 eval-multilingual-shortest complete: `artifacts/runs/opus55-screening-multilingual-shortest-eval`.

- School pipeline 2026-11-10T16:42:49.385523+00:00: Phase eval-multilingual-shortest archived at `artifacts/handoff/2026-11-10-opus55-school-eval-multilingual-shortest.zip` (SHA-256 `2e327bf7ada1f33897eeae6445084750ea6af6c631585af03d23e0c1dd8d31c9`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T16:46:31.058196+00:00: Step 7 eval-multilingual-feedback complete: `artifacts/runs/opus55-screening-multilingual-feedback-eval`.

- School pipeline 2026-11-10T16:46:31.175929+00:00: Phase eval-multilingual-feedback archived at `artifacts/handoff/2026-11-10-opus55-school-eval-multilingual-feedback.zip` (SHA-256 `526448c3cd73e76781ab2ef4b8d67b48bce7969f89872904103eefc8c667d5e2`). Back this up privately; Git does not carry artifacts.

- School pipeline 2026-11-10T16:46:32.425039+00:00: SCREENING finished. Report: `docs/pilots/2026-11-10-opus55-screening.md`; worksheets: `artifacts/human-review/pilot-20261110`. STOP before Step 9 until every selected rewrite has explicit human approval. Official testing remains unopened.

- School pipeline 2026-11-10T16:46:32.566023+00:00: Phase screening-complete archived at `artifacts/handoff/2026-11-10-opus55-school-screening-complete.zip` (SHA-256 `d994719b353456a25656bc1db264a6f1ff1d8bed0abb5a71814d4cd21ce8dcbf`). Back this up privately; Git does not carry artifacts.
