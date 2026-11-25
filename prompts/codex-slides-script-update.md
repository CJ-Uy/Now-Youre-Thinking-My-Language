# Slide and script update for the 4:10 presentation

Written 26 November 2026 after the paper revision. The deck source is not in this repository. Hand the block below to the assistant that rebuilds the deck and the presentation script.

Checked against the course predictions and the cached Qwen3-0.6B tokenizer: every number on slides 1–8.

The rebuilt deck and script are `output/pdf/presentation-slides.pdf` and `output/pdf/presentation-script.pdf`. They apply every change below. Backup slides 9 and 10 match the paper. One fix is still open: backup slide 11 says "Repeat estimate of 9–14 compute hours" and should say 9–13.

```text
TASK: Update the 8-slide deck and the presentation script for "Now You're Thinking My Language".
Keep the visual style, the 4:10 total and every time slot. Change only what is listed below.
Do not change any number that is not listed here. Never describe the English + Mandarin
rewrites as human-reviewed. Slides 9-11 are backup slides: make their names and numbers
match the rules below.

NAMING RULE
- Where a slide shows one adapter, label it "English shortest" or "English feedback".
- "Short English" stays only as the pool name on slide 4.
- Spoken lines may still say "short English".

SLIDE 1 - no slide change.
Script (Charles, 0:00-0:20):
Hi, I'm Charles, and this is Avner. We wanted to know if a small model could show its work
in fewer tokens. Avner, can you show the kind of translation that gave us the idea?

SLIDE 2 - no slide change.
Script (Avner, 0:20-0:50):
Hi, I'm Avner. My Chinese name is Wat King Ki. Take 缘分. It's the feeling that two people
were meant to meet. Qwen counts one token for the word and nine for that explanation.
So we wondered whether a model could pick a shorter expression and keep the same idea.

SLIDE 3 - no slide change.
Script (Avner, 0:50-1:20):
We narrowed it to short math problems so we could check the answer. Here, three notebooks
cost fifteen dollars. Both versions find the price of one, then multiply by four. Switching
from "unit price" to 单价 takes us from twenty-three tokens to twenty-one. Both still get
twenty dollars. On a tight budget, those two tokens could leave room for another step.
Charles, how did we test it?

SLIDE 4 - add one small line under the table:
"Meaning review: all 86 English picks human-approved. English + Mandarin picks: 10 of 86
human-approved, 76 AI-approved only."
Script (Charles, 1:20-2:00) - unchanged:
We picked GSM8K because each problem has a number we can check. We trained five Qwen
adapters on the same eighty-six problems. One saw the original solutions. For each language
pool, we either took the shortest valid rewrite or used feedback from the unchanged model
trying to finish a partial solution. Most mixed rewrites had AI approval only. Then the five
adapters and the unchanged model answered the same two hundred development questions at
three reasoning budgets.

SLIDE 5
- Title: "English shortest generated 47.8% fewer tokens"
- Bar label "Short English" -> "English shortest". Values stay 102.56 and 53.52.
- Sub-caption: "English shortest vs. original solutions"
- Add one line below the interval line:
  "Met both proposal targets on point estimates: at least 20% fewer tokens, at most a
  3-point accuracy loss."
Script (Charles, 2:00-2:40):
At the 128-token budget, the original adapter averaged about a hundred and three generated
tokens. Short English averaged fifty-four. That's about forty-eight percent fewer. Short
English got seventy-two right, compared with seventy-three for the original. On the point
estimates, that met the targets we set in our proposal. The count is close, and the
uncertainty still leaves room for a meaningful drop in accuracy. Avner, what changed when
we added Mandarin?

SLIDE 6
- Legend: "Short English" -> "English". Keep "English + Mandarin".
- Add text at the right of each row:
  Shortest selection: "-5.5 pp, 95% interval [-13.0, +1.5]"
  Feedback selection: "-3.5 pp, 95% interval [-10.5, +3.0]"
- Keep both existing footnote lines. Add a third:
  "One decoding run. An earlier 50-question decode on a different GPU reversed the direction."
Script (Avner, 2:40-3:15):
For Mandarin, we compare shortest with shortest and feedback with feedback. The mixed
adapters got fewer answers right here, but both intervals include zero. In an earlier check
on fifty questions with a different GPU, the direction flipped. So the accuracy effect is
still uncertain. Token use stayed about the same. We did see switching in the outputs. One
answer wrote "Albert 比 Joshua 多" and used an English label elsewhere.
Speaking cue - unchanged.

SLIDE 7 - replace the left column. Use monospace for the equations, exactly as written.
- Title and question line: unchanged.
- Left column heading: "English feedback"
  18/12=1.5
  120/1.5=80
  44 generated tokens
- Right column heading: "Mixed feedback"
  120/18=6
  38 generated tokens
- Caption: "The mixed output skipped the inches-to-feet conversion."
- Small note: "Both adapters used feedback selection. Equations excerpted from model
  outputs at budget 256."
Speaking cue: Point to the inches-to-feet conversion in the English feedback column.
Then hand back to Charles.
Script (Avner, 3:15-3:45):
We also wanted to see what could get lost in a shorter answer. The English feedback output
converts eighteen inches to one and a half feet before dividing. The mixed feedback output
skips that step and gets six instead of eighty. It's six tokens shorter, and losing the
conversion changes the answer. Charles, what did we take away from the pilot?

SLIDE 8
- Headline: "English shortest used 47.8% fewer tokens at budget 128."
- Keep "72 vs. 73 correct out of 200".
- Line: "At budget 256, original solutions reached 87 correct. English shortest stayed at 72."
- Line: "Mandarin changed what the models wrote. Its effect on accuracy remains uncertain."
- Add footer: "Development set only. One training seed, one decoding run. Official test
  not run."
Script (Charles, 3:45-4:10):
The clearest saving came from short English at the tight budget. At two fifty-six, the
original adapter got eighty-seven right and short English stayed at seventy-two. Allowing
Mandarin changed what the model wrote. We're still unsure about its effect on accuracy.
These are development results from one training seed and one decoding run. Thanks.

Q&A BACKUP LINES (script only, not on slides)
Q: How stable are these numbers?
A: Not fully. Before the course run, we decoded the same adapters on the first fifty of
these questions on a laptop GPU, with the same settings and seeds. The original adapter led
in both runs. English versus mixed flipped. Mixed was ahead on the laptop and behind on the
course GPU. That, and intervals that include zero, is why we call the language effect
uncertain.

Q: Did the original adapter get the seed question right?
A: No. It tried the conversion but divided a hundred and twenty by twelve where it should
have multiplied, and answered ten over eighteen. So unit trouble isn't unique to the short
answers. The mixed adapters skipped the conversion. The original adapter got it backwards.

Q: Did the unchanged model get it right?
A: It wrote the conversion and reached eighty, but its answer line didn't parse, so it
scored as wrong. That's why we report unparseable answers separately.

Q: Isn't 120 divided by 18 equal to 6.67?
A: Yes. The model wrote six, so that line also rounds down. The bigger problem is the
skipped conversion.

Q: Were the Mandarin rewrites checked?
A: Every rewrite passed our automatic answer and equation checks. For meaning, a human
approved all 86 English picks. In each mixed condition, a human approved 10 of the 86, and
the other 76 were approved only by an AI reviewer. In an earlier set of 40 candidates with
both reviews, that AI reviewer approved 2 of the 4 the bilingual reviewer rejected.
```
