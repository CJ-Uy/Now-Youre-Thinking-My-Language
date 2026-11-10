# Teacher meaning audit and human review queue

24 October 2026. **The user selected Opus 5.5 for future research.** GPT remains historical screening evidence. This practical choice follows slightly shorter Opus material (3.72% on average) and 86/144 strict-format student successes versus GPT's 83/144; it is not proof of general or semantic superiority.

This AI audit read all 160 candidates against their original questions and supplied solutions. It found three GPT-specific and five Opus-specific review items. The parallel Claude review raised two additional candidates; its disagreements are carried forward rather than suppressed. A shared source ambiguity affects another 16 candidates.

**Combined priority queue: 26 unique candidates (12 GPT, 14 Opus).** Ten are candidate-specific wording/dependency/terminology flags; sixteen belong to one shared source decision. All 160 remain `reviewed=false`. The other 134 have no specific flag in this combined queue and are not human-approved.

## Reading the list

Candidate indices are zero-based. Step and raw JSONL line numbers are one-based. Priority 1 means inspect first; priority 2 means clarify wording or terminology. These are human-review requests, not automatic rejection labels. The question and equations are part of the interpretation; recoverable shorthand and Mandarin-only multilingual text were not rejected merely for being compact.

All raw paths below are relative to `artifacts/teacher-comparison/chat-export-round1`.

## GPT-01: gpt61 / train-1458 / multilingual / 3

Priority 1. Raw file: `gpt61/raw/train-1458.jsonl`, line 8.

Exact text: step 2: `加前菜得税前述及的餐费($)`.

The garbled phrase introduces tax-before wording absent from the question and supplied solution. The unchanged equation does not justify adding that concept.

Human decision needed: Decide whether the added tax wording changes the intended explanation or makes it unusable. Keep the original response; record any rejection separately.

## OPUS-01: opus55 / train-1258 / multilingual / 2

Priority 1. Raw file: `opus55/raw/train-1258.jsonl`, line 7.

Exact text: step 1: `15本书共有谜题`.

The source explains 450 puzzles using 15 books and 30 puzzles per book. This candidate omits 30 per book and leaves only the inherited tautological equation 450=450. The question still supplies 30, so this is a potential explanation loss rather than a changed numeric answer.

Human decision needed: Decide whether the solution must retain the per-book quantity in its explanation, given that the frozen annotation itself cannot show the multiplication.

## CLAUDE-R313: gpt61 / train-4833 / english / 3

Priority 2. Raw file: `gpt61/raw/train-4833.jsonl`, line 4.

Exact text: step 1: `15 snakes determine the monkey total`; step 2: `30 monkeys determine the lion total`; step 3: `25 lions determine the panda total`; step 4: `33 pandas determine the dog total`.

Every step only says one count 'determines' the next total and never states the relation (twice, 5 fewer, 8 more, one third), so the label does not describe what the equation computes.

Human decision needed: Confirm whether the question and equations supply enough context or whether the prose itself needs clearer quantities/relations. The parallel model reviewers disagreed, and this audit initially treated it as recoverable shorthand; preserve that disagreement for human review.

## GPT-02: gpt61 / train-4833 / english / 1

Priority 2. Raw file: `gpt61/raw/train-4833.jsonl`, line 2.

Exact text: step 2: `Subtract 5 monkeys for the lion count`.

The intended relation is five fewer lions than the monkey count. Subtracting monkeys can sound like physically removing animals rather than comparing two species counts. The equation and question resolve the numeric intention.

Human decision needed: Confirm whether the wording clearly expresses a comparison of counts without implying removal of monkeys.

## GPT-03: gpt61 / train-4833 / multilingual / 3

Priority 2. Raw file: `gpt61/raw/train-4833.jsonl`, line 8.

Exact text: step 2: `狮子：猴数少五只`; step 3: `熊猫：狮数多八只`.

The missing comparison marker makes it less clear whose count is smaller or larger. The equations give the correct intended directions; this is a wording concern, not a claim that the arithmetic changed.

Human decision needed: Confirm that a reader understands lions are five fewer than monkeys and pandas eight more than lions.

## CLAUDE-R852: opus55 / train-1458 / multilingual / 3

Priority 2. Raw file: `opus55/raw/train-1458.jsonl`, line 8.

Exact text: step 1: `4 entrees 共`.

Step 1 '4 entrees 共' is a dangling fragment that never says the quantity (cost of the entrees).

Human decision needed: Confirm whether the question and equations supply enough context or whether the prose itself needs clearer quantities/relations. The parallel model reviewers disagreed, and this audit initially treated it as recoverable shorthand; preserve that disagreement for human review.

## OPUS-02: opus55 / train-4833 / multilingual / 3

Priority 2. Raw file: `opus55/raw/train-4833.jsonl`, line 8.

Exact text: step 2: `lions: 猴少5`; step 3: `pandas: 狮多8`.

Like GPT-03, the clipped Chinese comparison can attach fewer or more to the reference animal rather than the target. The equations preserve the correct direction.

Human decision needed: Confirm the intended comparative meaning is clear from the whole candidate, not just from reconstructing the equations.

## OPUS-03: opus55 / train-5032 / multilingual / 3

Priority 2. Raw file: `opus55/raw/train-5032.jsonl`, line 8.

Exact text: step 1: `half phone 手机`.

The phrase omits charge and time, making half phone ambiguous in isolation. The source concerns half of a full phone charging session, not half of the device. The equation and final minutes label help recover the intended meaning.

Human decision needed: Decide whether this shorthand clearly refers to charging the phone halfway.

## OPUS-04: opus55 / train-3457 / multilingual / 0

Priority 2. Raw file: `opus55/raw/train-3457.jsonl`, line 5.

Exact text: step 3: `铜币总数 = 银币 x 2`; step 4: `每箱铜币`.

The source says bronze coins. 铜币 can be a broad term for copper-based coins and does not explicitly retain the bronze alloy. This is a terminology question for a Mandarin reviewer, not a confirmed mistranslation.

Human decision needed: Confirm whether the generic term preserves the intended bronze category or is too imprecise.

## OPUS-05: opus55 / train-3457 / multilingual / 2

Priority 2. Raw file: `opus55/raw/train-3457.jsonl`, line 7.

Exact text: step 3: `铜币是银币的两倍`; step 4: `铜币平分到5箱`.

As in OPUS-04, the source bronze category is expressed only as generic 铜币. The coin counts and distributions remain unchanged.

Human decision needed: Confirm whether this term is acceptable for bronze in this training context.

## Shared source decision: train-3341

Source wording: `In the third week, 2000 more cases were recorded in the state.`

The phrase can mean an additional 2000 cases during week 3 or 2000 more than the previous week. The supplied worked solution and answer use 2000 as the week-3 count and total 9500. Every candidate follows that supplied interpretation; this is not a teacher-introduced error.

Confirm the supplied interpretation is acceptable or mark this source question for a matched eligibility decision affecting both arms. Do not edit its gold answer, prompts or raw responses in place.

| Arm | Question | Pool | Candidate indices |
|---|---|---|---|
| gpt61 | train-3341 | english | 0, 1, 2, 3 |
| gpt61 | train-3341 | multilingual | 0, 1, 2, 3 |
| opus55 | train-3341 | english | 0, 1, 2, 3 |
| opus55 | train-3341 | multilingual | 0, 1, 2, 3 |

These are 16 affected candidates but one source issue, not 16 teacher-introduced errors.

## Source quirks and audit limits

- All train-1258 variants correctly retain the supplied 450=450 annotation. Most retain the 15-books-by-30-puzzles relationship in words; OPUS-01 does not. Do not silently repair the frozen annotation.
- All train-3620 variants keep the unannotated fraction reasoning in text and have one equation step. Feedback ineligibility is not a meaning error.
- Both teachers retain train-1914's unusual dollars-per-watt units. No unit correction was made.
- Opus train-3457 multilingual candidates 1 and 3 retain the English word Bronze/bronze. OPUS-04/05 concern the variants using only the broader Chinese material term, whose acceptability needs a Mandarin reviewer.

The Codex auditor's session metadata was gpt-6.1-sol with xhigh effort. This conversation authored the GPT arm; identities and earlier feedback were known. It was not independent, blinded or human review. Every candidate was read. Checks covered entities, quantities, units, comparison directions, fractions, time references, totals versus per-item amounts, dependencies and unsupported additions. No human semantic pass rate is claimed.

The parallel review's five flagged rows were read from claude-pipeline-20261024/blind-review-unblinded-flags.json. Three overlapped this audit; two were added to the queue. The other reviewers' complete verdicts were not re-audited here. Their original files and differing assessments remain intact.

The full 160-candidate ledger, exact excerpts, rubric, provenance and subsequent user teacher decision are in meaning-audit-20261024/audit.json under the prompt pack. before.json contains 49 pre-existing file hashes. Raw responses, provenance, imports, scores and review flags were preserved. No responses were repaired or regenerated and no training or new student generation ran.

See [the measured comparison](2026-10-24-teacher-screening.md), [the experiment log](../EXPERIMENT_LOG.md) and [the Claude handoff](../CLAUDE_HANDOFF.md). Human decisions must be recorded separately; selecting Opus does not approve its candidates.
