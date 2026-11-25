# Opus 5.5 pilot — UNREVIEWED SCREENING

School RTX 2080 Ti, unchanged emulated-BF16 runtime. This screening establishes no final research result.

Matched training questions: 88. Training attempts: 2. Length penalty: 1.0.
All compared runs use `configs/pilot-opus55.json` (SHA-256 `4c2cce25f583d483688ba9013809c054509a8cfcfb9e3fe15d6e32fb9a305604`). First 50 development questions, budget 256; no official test.

| Condition | Correct / 50 | Accuracy | Mean tokens | Mean seconds | Runtime failures | Truncations | Unparseable |
|---|---:|---:|---:|---:|---:|---:|---:|
| unchanged | 18 | 0.360 | 136.68 | 5.878 | 0 | 2 | 19 |
| original | 25 | 0.500 | 113.02 | 8.241 | 0 | 1 | 0 |
| english-shortest | 23 | 0.460 | 56.5 | 4.617 | 0 | 1 | 1 |
| english-feedback | 24 | 0.480 | 54.1 | 4.453 | 0 | 0 | 1 |
| multilingual-shortest | 18 | 0.360 | 51.4 | 4.391 | 0 | 0 | 2 |
| multilingual-feedback | 23 | 0.460 | 51.44 | 4.260 | 0 | 0 | 1 |

All failures and truncations remain in the denominator. Missing token measurements remain missing.

## Paired comparisons

| Reference → candidate | Accuracy difference | 95% bootstrap interval | Output-token reduction |
|---|---:|---|---:|
| english-shortest → multilingual-shortest | -0.100 | [-0.26, 0.06] | 0.0902654867256637 |
| english-feedback → multilingual-feedback | -0.020 | [-0.16, 0.12] | 0.049168207024029575 |
| original → english-shortest | -0.040 | [-0.18, 0.1] | 0.5000884799150593 |
| original → english-feedback | -0.020 | [-0.16, 0.12] | 0.5213236595292868 |
| original → multilingual-shortest | -0.140 | [-0.3, 0.02] | 0.5452132365952929 |
| original → multilingual-feedback | -0.040 | [-0.2, 0.12] | 0.5448593169350557 |
| unchanged → original | 0.140 | [-0.04, 0.32] | 0.1731050629206906 |

## Student-tokenizer measurements

Earlier round-1 screening found that multilingual material was not shorter under the Qwen tokenizer. The current selected-input measurements are reported separately below; word counts are not used.

| Strategy | English mean training tokens | Multilingual mean training tokens |
|---|---:|---:|
| shortest | 61.000 | 59.875 |
| feedback | 63.080 | 62.261 |

Elapsed command wall time: 4.533 hours (includes loading and CPU comparison commands; not a GPU-utilization integral).
Raw outputs, adapters and manifests: `artifacts/runs/opus55-screening-*`. Selection exclusions: `artifacts/conditions/opus55-screening-20261110/selection-audit.json`.
Stability evidence: `artifacts/scores/opus55-calibration-first50-a8-20261110/stability.json`. Penalty table: `artifacts/scores/opus55-calibration-a2-20261110/penalty.json`.
Human worksheets: `artifacts/human-review/pilot-20261110`. No new ledger decisions or reviewed flags were inferred.
Next: collect named human A/R/U decisions, substitute rejected picks in a new selection, and obtain approval for every selected rewrite before the reviewed series.
Full development sweeps, human meaning approval, and official testing have not run. School/laptop timing is not a controlled comparison.
