# Opus 5.5 course GPU pilot

**AI-assisted, unreviewed, single seed.** Under the 128-token reasoning budget, the English-shortest adapter answered 72 of 200 questions correctly versus 73 for the original-solution adapter. Its outputs used 48% fewer tokens. The paired accuracy interval permits a loss as large as 7 percentage points. At budgets 256 and 512, the original-solution adapter answered 87 questions correctly and both English adapters lost 7.5–8.0 percentage points against it.

## Setup

The unchanged Qwen3-0.6B model and five saved LoRA adapters ran on the same RTX 2080 Ti on `ughost24`. Qwen thinking was disabled. All five adapters used the same 86 training IDs and training seed 42. Each English rewrite condition had recorded human approval for its 86 picks. In each multilingual rewrite condition, 10 picks had recorded human approval and 76 had AI approval only under H-0046. The latter retain `reviewed=false`. The sibling laptop report documents the training selection and quick check. [Laptop pilot and review provenance](2026-11-20-opus55-aiassist.md)

All six runs used the same 200 development questions, split manifest and generation config. The reasoning budgets were 128, 256 and 512, with up to 64 separate answer tokens. The course runtime supports BF16 through emulation on this GPU. The course series provides the within-hardware comparisons below. The laptop and course runs have distinct execution environments. [Run configuration](../../configs/pilot-opus55.json)

## Development results

The table includes every prediction, including unparseable answers and truncations. The latter categories can overlap. Seconds are mean elapsed generation time per question. Output tokens count generated reasoning and answer tokens.

| Budget | Condition | Correct / 200 | Accuracy | Mean output tokens | Mean seconds | Unparseable | Truncated | Runtime errors |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 128 | Unchanged Qwen | 41 | 20.5% | 123.53 | 6.05 | 112 | 93 | 0 |
| 128 | Original solutions | 73 | 36.5% | 102.56 | 8.29 | 12 | 59 | 0 |
| 128 | English shortest | 72 | 36.0% | 53.52 | 5.22 | 1 | 3 | 0 |
| 128 | English feedback | 71 | 35.5% | 57.26 | 5.10 | 3 | 4 | 0 |
| 128 | Multilingual shortest | 61 | 30.5% | 54.38 | 4.89 | 5 | 4 | 0 |
| 128 | Multilingual feedback | 64 | 32.0% | 53.83 | 4.82 | 4 | 3 | 0 |
| 256 | Unchanged Qwen | 66 | 33.0% | 142.56 | 6.61 | 87 | 14 | 0 |
| 256 | Original solutions | 87 | 43.5% | 113.59 | 9.20 | 2 | 2 | 0 |
| 256 | English shortest | 72 | 36.0% | 54.40 | 5.17 | 1 | 1 | 0 |
| 256 | English feedback | 71 | 35.5% | 58.73 | 5.00 | 3 | 2 | 0 |
| 256 | Multilingual shortest | 61 | 30.5% | 54.78 | 4.76 | 4 | 0 | 0 |
| 256 | Multilingual feedback | 64 | 32.0% | 55.14 | 4.81 | 4 | 2 | 0 |
| 512 | Unchanged Qwen | 63 | 31.5% | 146.69 | 6.68 | 88 | 1 | 0 |
| 512 | Original solutions | 87 | 43.5% | 114.18 | 8.85 | 2 | 0 | 0 |
| 512 | English shortest | 72 | 36.0% | 55.67 | 4.87 | 1 | 1 | 0 |
| 512 | English feedback | 71 | 35.5% | 61.28 | 5.15 | 3 | 2 | 0 |
| 512 | Multilingual shortest | 61 | 30.5% | 54.78 | 4.77 | 4 | 0 | 0 |
| 512 | Multilingual feedback | 64 | 32.0% | 57.70 | 4.86 | 4 | 2 | 0 |

## Paired comparisons

The accuracy change is candidate minus reference. Positive token reductions indicate shorter candidate outputs. Intervals use 2,000 paired question-bootstrap samples with seed 42. They capture uncertainty across development questions conditional on the saved adapters and decoding run.

| Budget | Reference → candidate | Accuracy change (pp) | 95% bootstrap interval (pp) | Output-token reduction |
|---:|---|---:|---:|---:|
| 128 | English shortest → Multilingual shortest | −5.5 | [−13.0, +1.5] | −1.6% |
| 128 | English feedback → Multilingual feedback | −3.5 | [−10.5, +3.0] | 6.0% |
| 128 | Original solutions → English shortest | −0.5 | [−7.0, +6.5] | 47.8% |
| 128 | Original solutions → English feedback | −1.0 | [−8.5, +6.5] | 44.2% |
| 128 | Original solutions → Multilingual shortest | −6.0 | [−13.5, +1.5] | 47.0% |
| 128 | Original solutions → Multilingual feedback | −4.5 | [−11.5, +2.5] | 47.5% |
| 128 | Unchanged Qwen → Original solutions | +16.0 | [+8.5, +24.0] | 17.0% |
| 256 | English shortest → Multilingual shortest | −5.5 | [−13.0, +1.5] | −0.7% |
| 256 | English feedback → Multilingual feedback | −3.5 | [−10.5, +3.0] | 6.1% |
| 256 | Original solutions → English shortest | −7.5 | [−14.0, −0.5] | 52.1% |
| 256 | Original solutions → English feedback | −8.0 | [−15.0, −0.5] | 48.3% |
| 256 | Original solutions → Multilingual shortest | −13.0 | [−20.5, −5.5] | 51.8% |
| 256 | Original solutions → Multilingual feedback | −11.5 | [−19.0, −4.0] | 51.5% |
| 256 | Unchanged Qwen → Original solutions | +10.5 | [+2.5, +18.5] | 20.3% |
| 512 | English shortest → Multilingual shortest | −5.5 | [−13.0, +1.5] | 1.6% |
| 512 | English feedback → Multilingual feedback | −3.5 | [−10.5, +3.0] | 5.8% |
| 512 | Original solutions → English shortest | −7.5 | [−14.0, −0.5] | 51.2% |
| 512 | Original solutions → English feedback | −8.0 | [−15.0, −0.5] | 46.3% |
| 512 | Original solutions → Multilingual shortest | −13.0 | [−20.5, −5.5] | 52.0% |
| 512 | Original solutions → Multilingual feedback | −11.5 | [−19.0, −4.0] | 49.5% |
| 512 | Unchanged Qwen → Original solutions | +12.0 | [+4.0, +20.0] | 22.2% |

## Interpretation and output review

- At budget 128, both English adapters came within one percentage point of the original adapter while cutting mean output tokens by 44–48%. Their paired intervals are too wide to establish equivalence.
- At budgets 256 and 512, all four compact conditions used 46–52% fewer tokens than the original adapter. The corresponding paired accuracy intervals excluded zero in the direction of lower accuracy.
- Both multilingual adapters had lower observed accuracy than their matched English adapters at all three budgets. All matched language accuracy intervals include zero. Multilingual feedback saved about 6% of output tokens relative to English feedback. Shortest-selection output lengths were close.
- At budget 256, 193 of 200 multilingual-shortest outputs and 191 of 200 multilingual-feedback outputs contained Han characters. The other conditions produced zero Han-containing outputs. The reading worksheet contains 48 raw outputs across eight matched questions at that budget. A human reader still has to assess language use and whether a missing gold intermediate reflects a skipped step or a valid alternative. [Private reading worksheet](../../artifacts/handoff/2026-11-21-opus55-aiassist-school-results/reading/worksheet.md)

## Run record

The queue finished at 06:27:20 Shanghai time on 21 November 2026, after 5 h 51 min 50 s of wall time. All six evaluation commands and seven comparison commands exited successfully. Local verification reproduced all 18 per-budget metric rows and 21 paired comparisons from the 3,600 raw predictions. The adaptations used one seed. The official test set remains reserved. [Verified metrics](../../artifacts/handoff/2026-11-21-opus55-aiassist-school-results/verified-metrics.json) · [Private results archive](../../artifacts/handoff/2026-11-21-opus55-aiassist-school-results/school-results.tar.gz) · [Saved adapters and input bundle](../../artifacts/handoff/2026-11-21-opus55-aiassist-school-inputs.zip)
