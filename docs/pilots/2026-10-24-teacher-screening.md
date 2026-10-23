# Teacher screening: 24 October 2026

**Status: both teacher arms validated and scored with the common pipeline.** All 160 candidates remain unreviewed. This is a ten-training-question screening round, not a student-training result or an established teacher winner.

## Matched common-pipeline comparison

On 24 October 2026 the user authorized validation, scoring and comparison, with the raw responses preserved, `reviewed=false` and no training. Fresh imports and scores are in `artifacts/teacher-comparison/chat-export-round1/common-pipeline-20261024/`; the earlier Opus-only audit below is preserved as a historical snapshot.

Both arms contain exactly 80 expected candidates, 40 per pool, for the same first ten locked training IDs. Both fresh `research rewrite` imports accepted 80/80 candidates. An additional audit verified every original annotated equation exactly and in order, since the common arithmetic validator compares equation structures rather than enforcing literal order. Input/prompt hashes and the pilot data lock match. No candidate was repaired, regenerated, removed or marked human-reviewed.

| Check | GPT-6.1 | Opus 5.5 |
|---|---:|---:|
| Expected candidates present | 80/80 | 80/80 |
| Arithmetic/structure passes | 80/80 | 80/80 |
| Exact equations in original order | 80/80 | 80/80 |
| Feedback-eligible candidates | 72/80 | 72/80 |
| Student attempts saved | 144 | 144 |
| Runtime errors / truncations | 0 / 0 | 0 / 0 |
| Unparseable final answers | 37 | 36 |
| Missing output-token measurements | 0 | 0 |
| Human-reviewed candidates | 0 | 0 |

The eight `train-3620` candidates per arm have only one annotated calculation. Their feedback is **unavailable**, because the current policy cannot retain an intermediate step and withhold the final step. They remain in the candidate and token summaries. The scorer's zero placeholder for an excluded prefix is not counted as an observed failed attempt. Both arms have the same nine feedback questions and 36 eligible candidates per language pool.

| Pool | GPT mean solution tokens | Opus mean solution tokens | GPT strict feedback success | Opus strict feedback success |
|---|---:|---:|---:|---:|
| English | 62.550 | 60.825 | 36/72 (50.00%) | 36/72 (50.00%) |
| Multilingual | 64.425 | 61.425 | 47/72 (65.28%) | 50/72 (69.44%) |
| Both pools | 63.488 | 61.125 | 83/144 (57.64%) | 86/144 (59.72%) |

Solution tokens are measured with the pinned Qwen3-0.6B tokenizer over `render_solution`, including its final answer marker and answer, without added special tokens. These are teaching-material lengths, not generated-token savings from a trained student. Token summaries include all ten questions and 40 candidates per pool. Opus's mean is 3.72% lower across these saved candidates; within each teacher, multilingual candidates are slightly longer than English candidates on average.

Feedback uses the unchanged Qwen3-0.6B checkpoint, no adapter, thinking disabled, the first half of the candidate's steps, two attempts per eligible candidate, reasoning budget 256 and answer budget 64. Both arms use seed 42 to derive identical per-ID/pool/index/attempt seeds, temperature 0.7, top-p 0.8 and top-k 20. Every sampled continuation is retained, including incorrect and unparseable answers. GPT ran first and Opus second, serially.

This success rate includes **answer-format compliance**. For example, English candidate 0, attempt 0 for `train-6312` produced `#### 18 apples.` in both arms. The numeric-only parser rejects it, although the number matches the gold answer. These outputs were not rescored as successes. The 37 and 36 unparseable answers must not be described as that many demonstrated arithmetic mistakes.

For uncertainty, candidate lengths and feedback rates are first averaged within each question. Paired bootstrap resampling uses ten question units for length and nine for feedback, with 2,000 resamples and seed 42. Candidate phrasings and attempts are not treated as independent questions. The differences below are **GPT minus Opus**:

| Measure | Observed difference | Question-bootstrap 95% interval |
|---|---:|---:|
| English solution tokens | +1.725 tokens | -1.700 to +4.700 |
| Multilingual solution tokens | +3.000 tokens | -0.750 to +6.300 |
| Both-pool solution tokens | +2.363 tokens | -1.063 to +5.350 |
| English feedback success | 0.00 percentage points | -15.28 to +13.89 |
| Multilingual feedback success | -4.17 percentage points | -16.67 to +9.72 |
| Both-pool feedback success | -2.08 percentage points | -11.11 to +6.25 |

Opus is slightly shorter and has three more successful sampled continuations in this collection. All these intervals include zero. The nine-question feedback comparison, two attempts per candidate and single collection per teacher do not establish which teacher is better. The intervals concern question resampling within this collection, not backend variation or repeated teacher generations.

## Per-question results

Lengths average all eight candidates for that question. Feedback combines both pools, with 16 attempts per eligible question and arm. `N/A` denotes no eligible prefix, not zero success.

| Question ID | GPT mean tokens | Opus mean tokens | GPT feedback | Opus feedback |
|---|---:|---:|---:|---:|
| train-1458 | 78.250 | 76.250 | 16/16 | 16/16 |
| train-3620 | 41.750 | 51.375 | N/A | N/A |
| train-6312 | 54.375 | 53.000 | 8/16 | 7/16 |
| train-4833 | 97.750 | 99.625 | 7/16 | 4/16 |
| train-5032 | 40.250 | 37.250 | 7/16 | 7/16 |
| train-1914 | 49.500 | 48.625 | 16/16 | 15/16 |
| train-1258 | 50.625 | 44.250 | 2/16 | 1/16 |
| train-5173 | 36.750 | 33.000 | 9/16 | 10/16 |
| train-3457 | 114.000 | 106.500 | 10/16 | 14/16 |
| train-3341 | 71.625 | 61.375 | 8/16 | 12/16 |

## Meaning review and collection limits

GPT's `train-1458`, multilingual candidate 3, contains the awkward unsolicited tax wording `税前述及`. Its original JSONL and separate failure record are preserved. The candidate passes mechanical validation and remains in this automatic screening; neither that pass nor successful student feedback establishes unchanged meaning. No semantic pass rate has been measured for either arm, and all 160 review flags remain false.

Both teachers read all ten prompts and wrote their responses in one repository-assistant conversation. Their harness instructions and effort settings differ: GPT's session metadata names `gpt-6.1-sol` with `xhigh` effort; Opus's harness reports `claude-opus-5-5` with extended reasoning and an effort value whose UI mapping is unknown. GPT had seen existing aggregate Opus audit status before generation. Backend snapshots, teacher sampling seeds, usage and cost remain unknown. These are limitations of the comparison, not settings inferred from the teacher names.

The student ran on an RTX 4060 Laptop GPU with Python 3.12.10, PyTorch 2.8.0+cu128 and Transformers 4.57.3. Pre-start GPU utilization and model memory were zero; observed GPU temperatures were 64 C before scoring and 66 C at one GPT sample. AC status, laptop power mode and continuous thermal conditions were not verified. Recorded student generation totals were 742.72 seconds for GPT prefixes and 624.19 seconds for Opus prefixes. Fixed run order and incomplete power/thermal control prevent a controlled speed or energy claim.

## Artifacts, reproduction and verification

The source commit recorded by both score manifests is `2c3cffbd337aaf2cc148b0baef8c42789fcab4f4`. The working tree was dirty; exact research-code/config hashes are saved in `run-context.json`, and those files were verified unchanged across scoring. Documentation updates and unrelated untracked media/output were not used as experiment inputs. At final handoff, concurrent changes to `scripts/compare_teachers.py` and `tests/test_teacher_pack.py` were also present; this run neither used nor modified them and did not test that separate utility.

Under `artifacts/teacher-comparison/chat-export-round1/common-pipeline-20261024/`:

- `preflight.json`: completeness, raw/provenance hashes, exact equation order and prefix exclusions.
- `gpt61-source.jsonl` and `opus55-source.jsonl`: unchanged candidate fields consolidated from each arm's first responses.
- `gpt61-import/` and `opus55-import/`: fresh common-validator imports and metadata.
- `gpt61-scores/` and `opus55-scores/`: `scored.jsonl`, all 144 `attempts.jsonl` records per arm, and manifests.
- `token-audit.json`: independent student-tokenizer measurements for every candidate.
- `comparison.json`: per-pool and per-question measurements, paired intervals and integrity results.
- `RUN.md` and `summarize.py`: exact commands, scope, interpretation and reproducible aggregation with assertions.

The saved comparison verified all 20 raw-response hashes and both original provenance hashes unchanged, every candidate field preserved through import/scoring, all review flags false, matching score settings/data/model revisions, all 288 attempt keys and seeds, feedback totals from sampled correctness, and tokenizer counts independently. No pipeline code, prompts, configuration or datasets were changed. No teacher-specific training, condition selection, calibration tuning or official-test evaluation ran. Human meaning review is the next required research step before training eligibility can be established.

All raw responses and scoring artifacts remain local and ignored; no screening data was published to the explainer. Back up the private artifact directory separately from Git.

## Independent reproduction and blind model review

A separate Claude session repeated the consolidation, import and scoring in `artifacts/teacher-comparison/chat-export-round1/claude-pipeline-20261024/`. All 288 attempts match the run above in seed, predicted answer and output-token count, so the measurements reproduce exactly. The GPU timings of the two runs overlapped and are not comparable.

`scripts/compare_teachers.py` applies the current selection rule (penalty 0.1, provisional) to each arm. It compares the selected training material on the nine questions both arms retain. Differences are GPT minus Opus:

| Rewritten condition | Mean token difference | Opus shorter / GPT shorter / tie | Feedback accuracy difference |
|---|---:|---:|---:|
| `english-shortest` | +2.67 | 6 / 1 / 2 | +0.22 |
| `english-feedback` | +2.00 | 5 / 2 / 2 | +0.11 |
| `multilingual-shortest` | +2.11 | 6 / 3 / 0 | 0.00 |
| `multilingual-feedback` | +0.78 | 6 / 3 / 0 | 0.00 |

For the blind wording review, two model reviewers (a Claude Sonnet and a Claude Opus subagent) received only an anonymized sheet. The sheet contained each question, its original solution and the 16 shuffled candidates under opaque codes. The teacher key was stored outside their directory. The reviewers' verdicts agreed on 157 of 160 candidates. These candidates need human review:

| Teacher | Question | Pool / index | Reviewers | Issue |
|---|---|---|---|---|
| GPT-6.1 | `train-1458` | multilingual 3 | both reject | Step 2 says `税前` (pre-tax), a tax the question never mentions; the wording is garbled |
| Opus 5.5 | `train-5032` | multilingual 3 | both review | Step 1 `half phone 手机` does not say what is halved (the charging time) |
| Opus 5.5 | `train-1458` | multilingual 3 | one review | Step 1 `4 entrees 共` is a dangling fragment that never names the cost |
| GPT-6.1 | `train-4833` | English 1 | one review | Step 2 `Subtract 5 monkeys` gives the 5 the wrong unit; there are 5 fewer lions than monkeys |
| GPT-6.1 | `train-4833` | English 3 | one review | Every step says one count "determines" the next and never states the relation |

The other 155 candidates were judged acceptable by both reviewers. This is a model screen, not human review, and one reviewer shares the Opus teacher's model family. All `reviewed` flags remain false. Unblinded flags and reviewer notes are in `blind-review-unblinded-flags.json`.

Neither teacher is established as better. Opus is marginally preferable on this screen: its material is slightly shorter in every rewritten condition and none of its candidates were rejected. GPT matched or exceeded Opus on selected-candidate feedback in the English conditions. Multilingual candidates were not shorter than English candidates for either teacher, which bears directly on the study's compression hypothesis.

## Earlier Opus-only output audit

| Check | Observed result |
|---|---:|
| Expected question response files present | 10 / 10 |
| Unique expected `(id, pool, candidate)` combinations | 80 / 80 |
| English candidates | 40 |
| Multilingual candidates | 40 |
| Arithmetic/structure validator passes | 80 / 80 |
| Exact annotated equations preserved in original order | 80 / 80 |
| Eligible for the current partial-solution prefix check | 72 / 80 |
| Marked human-reviewed | 0 |
| GPT response files at the initial Opus-only audit | 0 |

Verified the input and ten prompt hashes against the prepared manifest, all expected candidate indices 0–3 in each pool, unchanged final numeric answers, and stable response-file hashes during the audit. The existing `research rewrite` importer independently accepted all 80 candidates. Arithmetic validity does not establish unchanged meaning; human semantic review remains pending.

A static call to `feedback_prefix` accepts 72 candidates. The eight candidates for `train-3620` have only one annotated calculation, as required by the supplied source, so the current policy cannot withhold a final step while retaining an intermediate step. This is a source/prefix constraint, not missing or invalid Opus output. Apply the same policy to GPT and use common eligible IDs for downstream comparisons. No student feedback generations were run by this check.

Local artifacts:

- Prompt/input manifest: `artifacts/teacher-comparison/chat-export-round1/manifest.json`.
- Opus first responses and provenance: `artifacts/teacher-comparison/chat-export-round1/opus55/`.
- Consolidated candidates: `artifacts/teacher-comparison/chat-export-round1/opus55/candidates.jsonl`.
- Audit with response hashes and validation results: `artifacts/teacher-comparison/chat-export-round1/opus55/validation-audit.json`.
- Static prefix eligibility: `artifacts/teacher-comparison/chat-export-round1/opus55/prefix-audit.json`.
- Imported candidates and run metadata: `artifacts/rewrites/teacher-opus55-round1/`.

The provenance records Claude Code in the Claude desktop app, with its harness reporting Opus 5.5 / `claude-opus-5-5`. That is a reported label, not independent verification of a backend snapshot. All ten prompts were read and answered in one repository-assistant conversation. Custom session instructions were present; backend snapshot, decoding seed and token billing are unknown. Preserve these limits and use the same collection procedure for the GPT arm.

## Original collection handoff (completed above)

This is the earlier handoff text; its pending-status statements describe the time before GPT collection and scoring.

Collect the GPT arm in a fresh GPT-6.1 session using [the same teacher instruction](../../prompts/run-teacher-comparison.md), changing `ARM` to `gpt61`. Keep first outputs and failures, then perform the same audit and import. Compare meaning review, Qwen-token lengths and unchanged-student feedback before any downstream teacher-specific training. No student-feedback scoring or teacher-specific training has run for either arm yet.

These raw artifacts are ignored by Git and have not been uploaded. A teammate needs the private artifact archive to inspect exact teacher responses; the tracked prompt generator can reproduce the inputs, but a new chat response is a new stochastic sample.
