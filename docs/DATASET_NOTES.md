# GSM8K label and wording issues

Notes for the report's data and limitations sections. Updated 20 November 2026. "Found in this study" lists only what our teacher collection, AI pre-reviews and human review happened to surface in the 200 training-pool questions used so far: 100 pilot training and the first 100 calibration questions. This was not a systematic audit. The development split has not been examined this way.

## Published evidence that GSM8K labels contain errors

- Vendrow, Vendrow, Beery and Madry (2025), [Do Large Language Model Benchmarks Test Reliability?](https://arxiv.org/abs/2502.03461), arXiv:2502.03461. They describe older benchmarks as riddled with errors, giving GSM8K as an example at about 5%. They re-examined 300 GSM8K **test** questions and removed 26 as bad questions, 1 of them mislabelled (Table 2), to build a cleaned "platinum" subset.
- Truong et al. (2025), [Fantastic Bugs and Where to Find Them in AI Benchmarks](https://arxiv.org/abs/2511.16842), arXiv:2511.16842. Citing Vendrow et al., they state that about 5% of GSM8K questions are invalid. They use the "GSM8K-Platinum annotations" to label 88 of 997 questions invalid.
- hkust-nlp, [gsm8k-fix](https://huggingface.co/datasets/hkust-nlp/gsm8k-fix) (Hugging Face dataset). This corrects **training-split** labels. Errors were found by investigating unusually low pass rates of DeepSeekMath-7B-RL. The README lists 16 corrected training indices: 167, 474, 1081, 2338, 2620, 2770, 3263, 3529, 3995, 4099, 4105, 4796, 5598, 6768, 7182 and 7401. The maintainers hope the fix is exhaustive but do not claim it is.

Our question IDs are `train-<index>` in the pinned `openai/gsm8k` `main` revision `740312add88f781978c0658806c59bc2815b9866`. Two gsm8k-fix indices fall in our prepared calibration split: `train-3529`, which is among the 100 calibration questions used, and `train-2770`, which is not. Both contain the errors gsm8k-fix describes, which suggests the two numberings match. No gsm8k-fix index falls in the pilot training or development splits.

## Found in this study

### Wrong or doubtful gold answers

| ID | Split here | Problem | In gsm8k-fix? | Handling |
|---|---|---|---|---|
| `train-2867` | pilot training | "Micah runs 2/3 times as fast as Dean" (9 h) means Micah takes 9 ÷ 2/3 = 13.5 h, but the solution computes 9 × 2/3 = 6 h. The gold answer is 23; the speed reading gives 40.5. | No | Excluded from all five conditions in the reviewed series (decision `H-0045`). The 10 November screening series still contains it. |
| `train-228` | calibration | The question asks how many more employees drive (120) than take public transport (40), which is 80. The solution subtracts non-drivers instead (80 − 40) and gives 40. | No | Calibration only; no training effect. Noted as a limitation of the penalty calibration. |
| `train-1052` | calibration | "Tim is 5 years less than twice John's age", with Tim 79, gives John (79 + 5) / 2 = 42 and James 30. The solution uses 79 − 5 and gives 25. | No | Calibration only. |
| `train-3529` | calibration | The question says forty percent support the first team, but the solution uses 60%. | Yes | Calibration only. Our Opus teacher subagent flagged it independently. |
| `train-2770` | calibration split, not among the 100 used | The worked solution totals $108, but the gold answer line says 106. | Yes | Not scored or used. |

In the 200 questions used (100 training, 100 calibration), 4 gold answers (2.0%) are wrong or doubtful: `train-2867`, `train-228`, `train-1052` and `train-3529`. That is in line with the few-percent rates reported above. Three of the four are not in gsm8k-fix. Detection was incidental, so the true rate in our sample may be higher.

### Questions unusable for the method (no wrong answer)

- `train-3562`, `train-618`: the solutions have no `<<…>>` calculations, so no step-preserving rewrite exists. Excluded from all conditions.
- `train-394` (calibration): uses `//` floor division, which the validator rejects.
- One-calculation questions (9 in the pilot training set) cannot supply a feedback prefix. They are excluded from all conditions by user decision.

### Ambiguous wording (kept)

- `train-3341`: "2000 more cases" in week 3 can mean 2000 or 2000 more than week 2. Kept with the dataset's reading (decision `H-0001`).
- `train-1226`: "20 earrings" priced per pair; the solution treats it as 20 pairs.
- `train-2891`: the question mixes "seabed" and "riverbed".

### Typos in the worked solutions (answers correct)

Rewrites either keep these or fix them to match the question; human reviewers judge the wording.

- Training: `train-5160` ("ducks" for geese), `train-224` ("4000 + 2040" for 4080 + 2040), `train-7186` ("2 * 11 - 22"), `train-7373` (mislabelled terms in the last line), `train-2698` (garbled line), `train-3205` ("b = 180." where 18 is meant), `train-4779` ("shoes" for sandals), `train-7439` ("left eaten" in the question).
- Calibration: `train-2297` ("bracelets" for necklaces), `train-5571` ("Noah" for Mason), `train-1074` ("wide" for long), `train-7270` and `train-1793` (digit typos).

## How this affects the study

- Every exclusion applies to all five conditions, including the original-solution baseline, so label noise does not favour any condition. It does add noise to every condition's training signal and to development accuracy.
- The length-penalty calibration ran on 100 calibration questions that include three with wrong or doubtful gold answers (`train-3529`, `train-228`, `train-1052`). Removing them changes nothing that was decided: the penalty rule still chooses 1.0, and the stability measure (b) moves from 0.646 to 0.652, still above the 0.60 threshold, so training still uses 2 attempts. In this calibration data every penalty in the grid, from 0 to 1.0, gives the same feedback picks (token reduction 0 at every penalty), so the chosen 1.0 does not change any pick. This should be reported.
- The development and official test splits were not audited. Published audits estimate about 5% invalid test questions, so part of every model's measured failures will reflect bad labels. Our comparisons are paired on identical questions, so this affects absolute accuracy more than the differences between conditions.
