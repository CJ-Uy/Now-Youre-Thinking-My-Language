# Opus 5.5 laptop pilot — AI-assisted, unreviewed

On the first 50 development questions, the four compact adapters used 48–54% fewer output tokens than the adapter trained on original GSM8K solutions. The original-solution adapter answered 26 correctly. Multilingual feedback came closest among the compact conditions, with 24 correct at 55 tokens per answer versus 106 for the original. These are **AI-assisted, unreviewed, single-seed** screening results.

## Quick development check — AI-assisted, unreviewed, single seed

The six models answered the same first 50 development questions with a reasoning budget of 256 tokens and a separate answer budget of 64. Seconds are mean generation time per question on the laptop RTX 4060. Every prediction is included. Unparseable means the evaluator could not extract a numeric final answer. An output can be both unparseable and truncated.

| Condition | Correct / 50 | Accuracy | Mean output tokens | Mean seconds | Unparseable | Truncated | Runtime errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| Unchanged Qwen | 18 | 36% | 128.38 | 7.06 | 19 | 1 | 0 |
| Original solutions | 26 | 52% | 106.30 | 7.32 | 0 | 0 | 0 |
| English shortest | 15 | 30% | 48.60 | 3.82 | 0 | 0 | 0 |
| English feedback | 21 | 42% | 54.14 | 4.38 | 1 | 1 | 0 |
| Multilingual shortest | 23 | 46% | 53.10 | 6.86 | 2 | 1 | 0 |
| Multilingual feedback | 24 | 48% | 55.08 | 5.94 | 1 | 1 | 0 |

## Quick paired comparisons — AI-assisted, unreviewed, single seed

Accuracy differences are candidate minus reference in percentage points (pp). Positive token reductions mean the candidate produced fewer tokens. Each 95% interval comes from 2,000 paired bootstrap samples of the 50 questions with seed 42. It describes uncertainty across these questions, conditional on this training and decoding run.

| Reference → candidate | Accuracy difference (pp) | 95% interval (pp) | Output-token reduction |
|---|---:|---:|---:|
| English shortest → multilingual shortest | +16 | [0, +34] | −9.3% |
| English feedback → multilingual feedback | +6 | [−8, +22] | −1.7% |
| Original → English shortest | −22 | [−38, −6] | 54.3% |
| Original → English feedback | −10 | [−24, +4] | 49.1% |
| Original → multilingual shortest | −6 | [−20, +8] | 50.0% |
| Original → multilingual feedback | −4 | [−18, +10] | 48.2% |
| Unchanged → original | +16 | [−2, +32] | 17.2% |

Only the accuracy loss for English shortest against original has an interval that excludes zero. Both multilingual conditions answered more questions correctly than their English counterparts and generated longer answers on average. Both accuracy intervals include zero.

The [private presentation](../../artifacts/presentations/opus55-aiassist-laptop-quick/briefing.pptx) uses this quick check. Across all quick predictions, 49 of 50 multilingual-shortest outputs and all 50 multilingual-feedback outputs contained Han characters. The other four conditions produced none. The [private reading worksheet](../../artifacts/human-review/opus55-aiassist-laptop-quick-output-inspection/worksheet.md) pairs eight questions across all six conditions. It includes cases with missing intermediate values so a reader can distinguish an omitted step from a valid alternative calculation. Human assessments are pending.

## Training selection and review — AI-assisted, unreviewed

Opus 5.5 supplied the rewrites. The five adapters used the same 86 training IDs. The unchanged baseline used Qwen3-0.6B directly. Qwen thinking was disabled throughout. Each English strategy had recorded human approval for all 86 picks. Each multilingual strategy had 10 picks with existing human approval and 76 accepted solely by Claude Fable 5.2 under decision H-0046. Those 76 retain `reviewed=false`. The adapters trained with `--allow-unreviewed` and are ineligible for the official test. In an earlier bilingual check, Fable had approved two of the four rewrites a human reviewer rejected. [Review decisions](../EXPERIMENT_LOG.md#20-november-2026-ai-assisted-review-series-prepared-decision-h-0046)

In the **final laptop selection**, mean Qwen-tokenized solution lengths for English and multilingual picks were respectively **60.81 and 59.92** under shortest selection and **62.94 and 62.31** under feedback selection. These measurements count the selected solution text, excluding the prompt. Multilingual training solutions were slightly shorter on average under both strategies even though quick-check generated answers were longer. [Final selection](../../artifacts/conditions/opus55-ai-assisted-20261120-final/)

Across the calibration penalty grid from 0 to 1, every penalty selected the same candidates. The two-attempt feedback pick matched the eight-attempt pick in 64.6% of eligible calibration pools, clearing the 60% threshold for two attempts. Removing three doubtful calibration labels gave 65.2%. Four wrong or doubtful gold answers surfaced incidentally among the 200 training and calibration questions used. Only within-laptop comparisons use the same hardware and training selection. [Calibration and sensitivity](../EXPERIMENT_LOG.md#20-november-2026-sensitivity-check-calibration-without-wrong-label-questions) · [Dataset notes](../DATASET_NOTES.md)

## Full development sweep — AI-assisted, unreviewed, single seed

The unchanged model and the original-solution adapter each completed 200 development questions at reasoning budgets 128, 256 and 512 on the laptop. The owner closed the laptop queue and approved a separate course GPU sweep of all six models using the five saved adapters. The full six-model results are in the [course GPU pilot report](2026-11-21-opus55-aiassist-school.md).

## Run record

The laptop used seed 42 and source commit `615956b` with a dirty worktree. The pipeline status records the actual source and input hashes. The five training commands took 14 min 12 s in total and the six quick checks took 30 min 24 s in total, measured from command start to exit. Each `artifacts/runs/opus55-aiassist-laptop-<condition>-quick/` directory contains the manifest, raw predictions and summary. All 300 quick predictions have token and timing measurements. [Run configuration](../../configs/pilot-opus55.json) · [Quick paired comparisons](../../artifacts/runs/opus55-aiassist-laptop-quick-comparison.json)
