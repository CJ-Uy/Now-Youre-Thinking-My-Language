# Time and cost estimate

**Status: planning estimate, 24 October 2026.** The ranges below are derived from measured pilot rates plus the stated assumptions. They are not research results. Recompute them whenever the runtime, hardware, student model or data sizes change.

The instructor's feedback on the proposal noted that the core experiments had no estimated time or cost range. This document supplies one. See the [experiment log](EXPERIMENT_LOG.md) for the full feedback and the planned responses.

## Measured unit rates

All GPU figures come from one RTX 4060 Laptop GPU (8 GB) with Qwen3-0.6B, generating one sequence at a time with the current `research` runtime.

| Rate | Measured value | Source |
|---|---:|---|
| Feedback attempt (unchanged student, partial solution, up to 256 + 64 tokens) | 4.3 to 5.2 s mean | 288 screening attempts: 624.19 s and 742.72 s per 144 ([screening](pilots/2026-10-24-teacher-screening.md)) |
| Evaluation per question, unchanged model, budget 128 | 11.5 s mean | 29 predictions in the interrupted `pilot-unchanged` run |
| Evaluation per question, unchanged model, budget 256 | 13.8 s mean | `pilot-quick-unchanged`, 50 questions |
| Evaluation per question, unmerged LoRA adapter, budget 256 | 21.4 s mean | `pilot-quick-original-eval`, 50 questions |
| LoRA training | 188.2 s for 100 questions x 3 epochs (0.63 s per example-epoch); peak 2.0 GB VRAM | `pilot-original` ([baseline report](pilots/2026-10-24-original-baseline.md)) |
| Feedback-eligible questions | 9 of 10 | Screening; one-calculation questions have no feedback prefix |
| Teacher text per question | about 2,200 prompt characters; about 2,000 response characters for eight candidates | Round-1 Opus prompts and raw responses |
| Teacher session time | about 4 minutes for ten questions | Round-1 Opus provenance (05:17 session start, files written by 05:20:42) |

Generation runs at roughly 9 output tokens per second for the unchanged model and 5 per second with the unmerged adapter.

## Assumptions (not measured)

- Budget 512 costs up to 25% more time per question than budget 256. Most outputs already stop well before 256 tokens (mean 115 to 128). This gives 11.5 to 17 s per question for the unchanged model and 18 to 27 s for an adapter.
- Every rewritten-condition adapter runs at the measured original-adapter speed. Shorter outputs would make them faster.
- 90% of questions are feedback-eligible, as in screening. Each question has eight candidates.
- Training time grows linearly with examples. Rewritten solutions are shorter than the originals, so the original-solution rate errs on the high side.
- Teacher tokens: visible text at 3 to 4 characters per token, plus 1,000 to 4,000 hidden reasoning tokens per question. The hidden reasoning is the largest uncertainty in the teacher cost.
- Human meaning review takes 1 to 2 minutes per candidate.
- One training seed unless stated. The Qwen3-1.7B comparison is not included; a larger student would multiply every GPU figure.

## Estimate by stage

GPU hours on one laptop. The milestone column covers the 100-question pilot planned for 29 October. The expansion column adds the remaining work for the 1,000-question study.

| Stage | Work | Milestone pilot | Expansion adds |
|---|---|---:|---:|
| Feedback scoring, two attempts | (training + 300 calibration questions) x 0.9 x 8 candidates x 2 | 6.9 to 8.3 h | 15.5 to 18.7 h (900 more training questions) |
| Repeated-scoring check | 50 calibration questions x 0.9 x 8 candidates x 8 attempts | 3.4 to 4.2 h | none |
| LoRA training | 5 conditions x 3 epochs | about 0.2 h (four remaining adapters) | 2.6 h (31 min per adapter) |
| Quick development check | base + 5 adapters x 50 questions x budget 256 | 1.4 to 2.1 h | none |
| Full development sweep | base + 5 adapters x 200 questions x 3 budgets | 16.9 to 25.3 h if run at the pilot | 16.9 to 25.3 h for the expanded adapters |
| Transfer set | base + 5 adapters x 200 questions x 3 budgets | none | 16.9 to 25.3 h |
| Official test | base + 5 adapters x 1,319 questions x 3 budgets | none | 111.6 to 167.1 h |

Totals:

- **Milestone pilot with the quick development check: about 12 to 15 GPU hours.** With the full development sweep instead: about 27 to 38 hours.
- **Complete study, one seed, current runtime: about 174 to 252 GPU hours**, or 7 to 10.5 days of continuous running on one laptop. The official test alone accounts for about two-thirds of this.
- **Complete study, three seeds: about 440 to 645 GPU hours** (18 to 27 continuous laptop-days). This does not fit the schedule before the 24 to 26 November presentations without runtime changes.

Evaluation, not training, dominates the cost. All five training runs together take under three hours.

## Teacher cost

The round-1 Opus responses were collected through the user's existing Claude subscription in a repository-assistant conversation. That route has no per-token charge but is subject to usage limits. At about 4 to 10 minutes per ten-question batch, including checks, the remaining 1,290 questions (990 training, 300 calibration) need roughly 9 to 22 hours of session time spread over several days.

For comparison, the hosted API at the Opus 5.5 list price ($4 per million input tokens, $20 per million output tokens, checked 24 October 2026) would cost:

| Scope | Questions | Standard API | Batch API (50% discount) |
|---|---:|---:|---:|
| Milestone pilot (90 remaining training + 300 calibration) | 390 | $13 to $38 | $6 to $19 |
| Complete study | 1,290 | $43 to $126 | $21 to $63 |

Allow about 20% more for retries. API spending needs an agreed team budget and a recorded decision. Switching from the subscription conversation to the API also changes the collection procedure, which must be fixed before the 100-question round.

The laptops are already owned, so GPU work has no rental cost. Power draw was not measured.

## Human review time

Arithmetic validation does not establish unchanged meaning, so review time must be planned explicitly.

| Review scope at 1,000 training questions | Candidates | Time at 1 to 2 min each |
|---|---:|---:|
| Every candidate (training only) | 8,000 | 133 to 267 h |
| Every candidate selected for training | about 3,000 | 50 to 100 h |
| 10% sample of selected candidates | about 300 | 5 to 10 h |

The selected-candidate count assumes about three unique picks per question. In screening, the feedback rule chose the same candidate as the shortest rule in 9 of 18 Opus pools.

## Options that need a decision

None of these has been tested or adopted. Each changes either the runtime or the protocol, so record a decision before using it.

1. **Merge adapters for evaluation.** If a merged adapter runs at the unchanged model's speed, the one-seed official test falls from 112 to 167 hours to 76 to 112 hours. Check on development questions that merging does not change the outputs.
2. **One budget on the official test.** Run all three budgets on development and only the frozen primary budget on the official test. With merged adapters, the one-seed official test would take about 25 to 37 hours. This changes the proposal's evaluation plan.
3. **Batched generation.** Throughput of 5 to 9 tokens per second for a 0.6B model, and the earlier finding that 24 CPU threads beat one (6.0 s against 10.7 s per question), suggest overhead-bound generation. Batching could be several times faster, but this has not been measured. Batching changes the per-question random streams, so apply it to every condition and rerun the reference.
4. **Fewer seeds or a smaller test subset.** Either reduces the claims the report can make.

Elapsed time is itself a reported measurement. If both laptops share the work, run every condition's timed evaluation on the same machine, or shard the questions identically across machines for every condition. Otherwise hardware differences become condition differences.
