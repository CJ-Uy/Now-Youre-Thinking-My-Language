// Builds the course paper as a Word document. The paper text lives in this file.
// Table numbers come from verified.json, which verify_numbers.py recomputes from the
// saved predictions and paired comparisons.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, AlignmentType,
  WidthType, BorderStyle, Footer, PageNumber, ExternalHyperlink, Math: OMath, MathRun,
  MathFraction, MathSubScript, HeadingLevel, VerticalAlign, PageBreak,
} = require("docx");

// Usage: node paper/build_paper.js [output.docx]
const verifiedPath = path.join(__dirname, "verified.json");
const figDir = path.join(__dirname, "figures");
const outPath = process.argv[2] || path.join(__dirname, "..", "output", "docx", "paper.docx");
const V = JSON.parse(fs.readFileSync(verifiedPath, "utf8"));

const BODY = { ascii: "Cambria", hAnsi: "Cambria", cs: "Cambria", eastAsia: "Microsoft YaHei" };
const SANS = { ascii: "Calibri", hAnsi: "Calibri", cs: "Calibri", eastAsia: "Microsoft YaHei" };
const MONO = { ascii: "Consolas", hAnsi: "Consolas", cs: "Consolas", eastAsia: "Microsoft YaHei" };
const INK = "182838";
const LINK = "000073";
const CONTENT_W = 9298; // A4 width minus two 1304-DXA margins

// Inline markup: `code`, **bold**, *italic*, ~sub~, ^sup^.
function runs(text, base = {}) {
  const out = [];
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*|~[^~]+~|\^[^^]+\^)/g).filter((p) => p !== "");
  for (const part of parts) {
    const curly = (s) => s.replace(/'/g, "’");
    if (part.startsWith("`")) out.push(new TextRun({ ...base, text: part.slice(1, -1), font: MONO, size: (base.size || 22) - 2 }));
    else if (part.startsWith("**")) out.push(new TextRun({ ...base, text: curly(part.slice(2, -2)), bold: true }));
    else if (part.startsWith("*")) out.push(new TextRun({ ...base, text: curly(part.slice(1, -1)), italics: true }));
    else if (part.startsWith("~")) out.push(new TextRun({ ...base, text: part.slice(1, -1), subScript: true }));
    else if (part.startsWith("^")) out.push(new TextRun({ ...base, text: part.slice(1, -1), superScript: true }));
    else out.push(new TextRun({ ...base, text: curly(part) }));
  }
  return out;
}

const P = (text, opts = {}) => new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 115 }, ...opts, children: runs(text, opts.run) });
const small = (text, opts = {}) => P(text, { ...opts, run: { size: 20, ...(opts.run || {}) } });
const H1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(text)] });
const H2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] });
const centered = (text, run, spacing = { after: 60 }) => new Paragraph({ alignment: AlignmentType.CENTER, spacing, children: runs(text, run) });
const caption = (label, text, opts = {}) => small(`**${label}:** ${text}`, { spacing: { before: 60, after: 220 }, ...opts });

function figure(file, widthPt, heightPt) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    keepNext: true,
    spacing: { before: 160, after: 40 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(figDir, file)), transformation: { width: Math.round((widthPt * 96) / 72), height: Math.round((heightPt * 96) / 72) } })],
  });
}

// Booktabs-style tables: rules above the header, below the header and below the last row.
const NONE = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const rule = (size, color = "000000") => ({ style: BorderStyle.SINGLE, size, color });
function tcell(text, width, o = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    columnSpan: o.span,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: o.padTop ?? o.pad ?? 25, bottom: o.pad ?? 25, left: 60, right: 60 },
    borders: { top: o.top || NONE, bottom: o.bottom || NONE, left: NONE, right: NONE },
    children: [new Paragraph({ alignment: o.align || AlignmentType.LEFT, spacing: { after: 0 }, children: runs(text, { size: 20, bold: o.bold, font: o.font }) })],
  });
}
function table(widths, rows, tableWidth = CONTENT_W) {
  return new Table({
    width: { size: tableWidth, type: WidthType.DXA },
    columnWidths: widths,
    alignment: AlignmentType.CENTER,
    borders: { top: NONE, bottom: NONE, left: NONE, right: NONE, insideHorizontal: NONE, insideVertical: NONE },
    rows: rows.map((r) => new TableRow({ cantSplit: true, tableHeader: r.header, children: r.cells })),
  });
}

const NAME = { unchanged: "Unchanged Qwen", original: "Original solutions", "english-shortest": "English shortest", "english-feedback": "English feedback", "multilingual-shortest": "Multilingual shortest", "multilingual-feedback": "Multilingual feedback" };
const SHORT = { ...NAME, unchanged: "Unchanged", original: "Original" };
const CONDS = Object.keys(NAME);
const minus = (s) => String(s).replace("-", "−");
const signed = (x) => (x > 0 ? "+" : x < 0 ? "−" : "") + Math.abs(x).toFixed(1);
const R = AlignmentType.RIGHT;
const C = AlignmentType.CENTER;
const A = (budget, cond) => V.appendix_a.find((r) => r[0] === budget && r[1] === cond);

function table1() {
  const w = [2500, 1133, 1133, 1133, 1133, 1133, 1133];
  const rows = [
    { header: true, cells: [tcell("", w[0], { top: rule(10) }), tcell("Exact-answer accuracy (%)", w[1] * 3, { span: 3, align: C, top: rule(10), bottom: rule(4) }), tcell("Mean generated tokens", w[1] * 3, { span: 3, align: C, top: rule(10), bottom: rule(4) })] },
    { header: true, cells: ["Condition", "128", "256", "512", "128", "256", "512"].map((t, i) => tcell(t, w[i], { align: i ? R : undefined, bottom: rule(6) })) },
  ];
  CONDS.forEach((cond, i) => {
    const bold = cond === "original" || cond === "english-shortest";
    const last = i === CONDS.length - 1 ? { bottom: rule(10) } : {};
    const acc = [128, 256, 512].map((b) => A(b, cond)[4].toFixed(1));
    const tok = [128, 256, 512].map((b) => A(b, cond)[5].toFixed(2));
    rows.push({ cells: [tcell(NAME[cond], w[0], { bold, ...last }), ...[...acc, ...tok].map((t, j) => tcell(t, w[j + 1], { align: R, bold, ...last }))] });
  });
  return table(w, rows);
}

function tableA() {
  const w = [800, 2400, 900, 950, 950, 950, 850, 800, 698];
  const head = ["Budget", "Condition", "Correct", "Acc. (%)", "Tokens", "Seconds", "Unpar.", "Trunc.", "Errors"];
  const rows = [{ header: true, cells: head.map((t, i) => tcell(t, w[i], { pad: 8, align: i === 1 ? undefined : R, top: rule(10), bottom: rule(6) })) }];
  V.appendix_a.forEach((r, i) => {
    const [budget, cond, , correct, acc, tokens, seconds, unpar, trunc, errors] = r;
    const o = { pad: 8, padTop: i % 6 === 0 && i ? 80 : 8, ...(i === V.appendix_a.length - 1 ? { bottom: rule(10) } : {}) };
    const vals = [String(budget), NAME[cond], String(correct), acc.toFixed(1), tokens.toFixed(2), seconds.toFixed(2), String(unpar), String(trunc), String(errors)];
    rows.push({ cells: vals.map((t, j) => tcell(t, w[j], { align: j === 1 ? undefined : R, ...o })) });
  });
  return table(w, rows);
}

function tableB() {
  const w = [800, 3900, 1400, 1700, 1498];
  const head = ["Budget", "Reference → candidate", "Δ acc. (pp)", "95% interval (pp)", "Token reduction (%)"];
  const rows = [{ header: true, cells: head.map((t, i) => tcell(t, w[i], { pad: 8, align: i === 1 ? undefined : R, top: rule(10), bottom: rule(6) })) }];
  V.appendix_b.forEach((r, i) => {
    const [budget, ref, cand, diff, lo, hi, red] = r;
    const o = { pad: 8, padTop: i % 7 === 0 && i ? 80 : 8, ...(i === V.appendix_b.length - 1 ? { bottom: rule(10) } : {}) };
    const vals = [String(budget), `${SHORT[ref]} → ${SHORT[cand]}`, signed(diff), `[${signed(lo)}, ${signed(hi)}]`, minus(red.toFixed(1))];
    rows.push({ cells: vals.map((t, j) => tcell(t, w[j], { align: j === 1 ? undefined : R, ...o })) });
  });
  return table(w, rows);
}

function exampleTable() {
  const w = [2700, 2700];
  const row = (a, b, o = {}) => ({ cells: [tcell(a, w[0], o), tcell(b, w[1], o)] });
  return table(w, [row("**Short English**", "**With a Mandarin label**"), row("unit price = 15 ÷ 3 = 5", "单价 = 15 ÷ 3 = 5"), row("unit price × 4 = 20", "单价 × 4 = 20"), row("23 tokens", "21 tokens", { padTop: 70 })], 5400);
}

const formula = new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 60, after: 160 },
  children: [new OMath({ children: [new MathRun("a(c) − λ "), new MathFraction({ numerator: [new MathRun("T(c)")], denominator: [new MathSubScript({ children: [new MathRun("T")], subScript: [new MathRun("max")] })] }), new MathRun(" .")] })],
});

const REFS = [
  ["Daniel Kleinman and Tamar H. Gollan. 2016. ", "Speaking Two Languages for the Price of One: Bypassing Language Control Mechanisms via Accessibility-Driven Switches", ". *Psychological Science*, 27(5), 700–714.", "https://doi.org/10.1177/0956797616634633"],
  ["Karl Cobbe et al. 2021. ", "Training Verifiers to Solve Math Word Problems", ". arXiv:2110.14168.", "https://arxiv.org/abs/2110.14168"],
  ["Freda Shi et al. 2023. ", "Language Models are Multilingual Chain-of-Thought Reasoners", ". ICLR.", "https://arxiv.org/abs/2210.03057"],
  ["Sanchit Ahuja, Praneetha Vaddamanu, and Barun Patra. 2025. ", "EfficientXLang: Towards Improving Token Efficiency Through Cross-Lingual Reasoning", ". arXiv:2507.00246.", "https://arxiv.org/abs/2507.00246"],
  ["Heming Xia, Chak Tou Leong, Wenjie Wang, Yongqi Li, and Wenjie Li. 2025. ", "TokenSkip: Controllable Chain-of-Thought Compression in LLMs", ". EMNLP.", "https://aclanthology.org/2025.emnlp-main.165/"],
  ["Kumar Tanmay, Kriti Aggarwal, Paul Pu Liang, and Subhabrata Mukherjee. 2025. ", "ORION: Teaching Language Models to Reason Efficiently in the Language of Thought", ". arXiv:2511.22891.", "https://arxiv.org/abs/2511.22891"],
  ["An Yang et al. 2025. ", "Qwen3 Technical Report", ". arXiv:2505.09388.", "https://arxiv.org/abs/2505.09388"],
  ["Edward J. Hu et al. 2022. ", "LoRA: Low-Rank Adaptation of Large Language Models", ". ICLR.", "https://arxiv.org/abs/2106.09685"],
  ["Joshua Vendrow, Edward Vendrow, Sara Beery, and Aleksander Madry. 2025. ", "Do Large Language Model Benchmarks Test Reliability?", ". arXiv:2502.03461.", "https://arxiv.org/abs/2502.03461"],
];
const reference = ([before, title, after, link], i) => new Paragraph({
  spacing: { after: 90 },
  indent: { left: 400, hanging: 400 },
  children: [...runs(`[${i + 1}] ${before}`, { size: 20 }), new ExternalHyperlink({ link, children: [new TextRun({ text: title, size: 20, color: LINK })] }), ...runs(after, { size: 20 })],
});

const F = JSON.parse(fs.readFileSync(path.join(figDir, "sizes.json"), "utf8"));
const fig = (n) => figure(`figure${n}.png`, F[`figure${n}`].pt[0], F[`figure${n}`].pt[1]);

const children = [
  centered("Now You're Thinking My Language", { font: SANS, bold: true, size: 46, color: INK }, { after: 80 }),
  centered("Learning Compact Multilingual Reasoning Dialects", { font: SANS, size: 24, color: INK }, { after: 0 }),
  centered("for Small Language Models", { font: SANS, size: 24, color: INK }, { after: 200 }),
  centered("Charles Joshua T. Uy and Wat King Ki", { size: 24 }, { after: 80 }),
  centered("COMP 4901B Large Language Models • HKUST", { size: 20 }, { after: 80 }),
  centered("21 November 2026", { size: 20 }, { after: 280 }),
  centered("**Abstract**", { size: 20 }, { after: 100 }),
  small("Short worked solutions can reduce the number of tokens a model generates, but their value depends on what the model can still solve. We fine-tuned Qwen3-0.6B on 86 matched GSM8K questions using original solutions and four compact variants that varied the language pool and selection rule. We evaluated the five adapters and the unchanged model on the same 200 development questions at reasoning budgets of 128, 256, and 512 tokens. At budget 128, the shortest-English adapter answered 72 questions correctly versus 73 for the original-solution adapter and used 47.8% fewer output tokens. On point estimates, both compact English adapters met the proposal's targets at this budget, a token reduction of at least 20% with an accuracy loss of at most three points. The paired 95% interval for the accuracy difference was [−7.0, +6.5] percentage points. At 256 and 512, every compact adapter used roughly half as many output tokens and answered fewer questions correctly than the original adapter. The adapters trained on English–Mandarin rewrites wrote Han characters in more than 95% of their outputs. The paired accuracy intervals against the corresponding English adapters included zero. These results describe a development pilot with a single training seed and a single decoding run. In each English–Mandarin condition, 76 of the 86 training rewrites were approved only by an AI reviewer.", { indent: { left: 546, right: 546, firstLine: 300 }, spacing: { after: 240 } }),

  H1("1 Introduction"),
  P("We started with words that are hard to translate directly. A word in Mandarin can take a phrase or even several sentences to explain in English. We wondered if a model could save tokens by choosing the shorter expression. Kleinman and Gollan found that bilingual speakers could switch to a more accessible word in a picture-naming task without a measurable cost in that setting [1]. That gave us a reason to test what a choice of language could do for a small model writing out a solution."),
  P("We focused on small models with tight token budgets. If three notebooks cost fifteen dollars, how much do four cost? We can reuse the price of one notebook in either language."),
  exampleTable(),
  P("We used the Qwen3-0.6B tokenizer to count the two lines of math.", { spacing: { before: 130, after: 130 } }),
  P("We narrowed the experiment to short arithmetic problems from GSM8K because each problem has a numeric answer we can check. We compared matched original solutions and compact rewrites, using the same training questions throughout. The compact English baseline shows what shortening alone can do. Comparing it with rewrites that also allow Mandarin under the same selection rule lets us ask what the second language adds."),
  P("The pilot ran from teacher rewrites to 3,600 scored outputs with no runtime errors. At the tightest budget, the shortest-English adapter generated 47.8% fewer tokens and answered 72 of 200 questions correctly, against 73 for the original solutions. The adapters trained on English–Mandarin rewrites wrote in the mixed style they were trained on. What the second language does to accuracy is still open."),

  H1("2 Related work"),
  P("GSM8K was introduced to evaluate grade-school arithmetic word problems with worked solutions [2]. Its annotations give us a concrete way to check that a teacher has retained the calculations during a rewrite. Shi et al. studied multilingual chain-of-thought prompting by translating GSM8K problems into several languages [3]. Our evaluation keeps the English questions fixed and varies the language permitted in the written solutions used for fine-tuning. This lets us observe changes in model outputs under the same prompts."),
  P("Other work motivates both parts of the comparison. EfficientXLang measured how reasoning language affects token use in reasoning models and found that results depend on the model and language [4]. TokenSkip teaches models to produce compressed traces through token selection [5]. ORION trains models to use compact symbolic forms and further optimizes for shorter reasoning [6]. We use supervised adaptation with teacher rewrites and a matched English control. This design lets us distinguish the observed benefit of shortening solutions from the difference associated with allowing Mandarin."),

  H1("3 Method"),
  H2("3.1 Data and candidate validation"),
  P("We used the main configuration of GSM8K. Its official training pool contains 7,473 questions and its official test set contains 1,319 [2]. We used seed 42 to prepare disjoint groups of 100 pilot training questions, 300 calibration questions, and 200 development questions from the official training pool. Candidate scoring and penalty calibration used the first 100 calibration questions. The eight-attempt stability check used the first 50 calibration questions. Only the retained pilot training questions contributed to adapter updates."),
  P("The teacher, labelled Claude Opus 5.5 in the collection records, was asked for four versions in English with equations and four allowing English, Mandarin, and equations. We call these the English pool and the multilingual pool. The teacher saw the question and its supplied solution. We verified that each rewrite preserved the numeric answer and the multiset of annotated calculations and that each equation evaluated correctly. A line could still attach the correct number to the wrong quantity, which required a separate meaning review."),
  P("We excluded 14 of the 100 training questions from every condition. Eleven had zero or one annotated calculation, which prevented a valid partial-solution probe. One had no eligible multilingual candidate without possible answer leakage in its prefix. A second had a doubtful source answer. AI review rejected all four Mandarin candidates for a third question because they omitted the meaning of a quantity. Removing the same questions from the original baseline kept all five adapters on the same 86 prompts."),
  P("All 86 selected English rewrites per strategy had recorded human approval. In each multilingual strategy, 10 selected rewrites had recorded human approval and 76 were accepted solely by Claude Fable 5.2 under the project's H-0046 decision. The 76 kept their unreviewed flags. In an earlier set of 40 Mandarin candidates with both reviews, the model approved two of the four candidates rejected by the bilingual reviewer. The difference in review coverage limits what we can attribute to language choice alone."),

  H2("3.2 Selecting a rewrite"),
  P("The shortest rule uses the candidate with the smallest Qwen-tokenized solution length within its pool. For the feedback rule, the unchanged Qwen3-0.6B reads the question and the first half of the candidate's steps. We withhold the final answer and reject prefixes that appear to reveal it. We check the final answer over two sampled completions. With *a*(*c*) the proportion of correct completions, *T*(*c*) the length of the rendered solution and *T*~max~ the longest eligible candidate in the pool for that question, we rank by", { spacing: { after: 60 } }),
  formula,
  P("Higher scores win, and fewer tokens break ties. We break remaining ties by candidate index in both rules. The feedback probe measures how the unchanged model completes a supplied prefix. The fine-tuned model later has to write its own steps from the question."),
  P("We used the preplanned repeat check to decide whether two attempts were enough for the pilot. At the check's fixed penalty of *λ* = 0.1, the first two completions selected the same winner as all eight in 62 of 96 eligible question-and-language pools (64.6%), above our preselected 60% threshold. The four separate two-attempt blocks agreed on the same winner in only 37 of 96 pools (38.5%). Removing three doubtful calibration labels raised two-versus-eight agreement to 65.2%. The first comparison justified keeping two attempts under our rule. The block comparison shows how often the winner can change with a different pair of completions."),
  P("The separate penalty calibration selected *λ* = 1.0 for the final conditions. Every tested penalty from zero through one selected the same candidates in the calibration data. This gives us a comparison between feedback-guided candidate choice and choosing by length alone, with no observed extra savings from increasing the penalty in calibration."),

  H2("3.3 Training and evaluation"),
  P("We trained Qwen3-0.6B [7] using low-rank adaptation (LoRA), which updates small trainable matrices while freezing the base weights [8]. We used one adapter with original GSM8K solutions and four compact conditions formed by crossing two language pools with two selection rules. Each adapter used three epochs, learning rate 2 × 10^−4^, batch size one, gradient accumulation over eight examples, LoRA rank eight, *α* = 16, dropout 0.05, and a maximum training sequence length of 1,024. We applied LoRA to linear layers, masked the prompt out of the training loss, and disabled Qwen thinking mode. The training and data seed was 42."),
  P("The unchanged model and the adapters received the same question-only prompt and budgets of 128, 256, and 512 generated reasoning tokens. Each run then generated up to 64 answer tokens. The evaluator supplied the answer delimiter if necessary and parsed the final number from the answer continuation. Sampling used temperature 0.7, top-*p* 0.8, and top-*k* 20, with seed 42 + *i* for question index *i* across conditions. Keeping both generation stages fixed allowed us to compare the six conditions on 3,600 outputs."),
  P("Accuracy is exact numeric agreement over all 200 questions per condition and budget. The denominator includes unparseable and truncated examples. We count generated reasoning and answer tokens, excluding the prompt and any inserted separator. We time both stages with GPU synchronization. To compare accuracy, we resample the same questions in both conditions, using 2,000 paired bootstrap replicates with seed 42. The intervals are conditional on these adapters and decoding draws."),

  H2("3.4 Compute environment"),
  P("We trained the five LoRA adapters on an NVIDIA GeForce RTX 4060 Laptop GPU with 8 GB of VRAM. We transferred the saved adapters and fixed evaluation inputs to the HKUST course cluster. On the allocated Linux node `ughost24`, one NVIDIA GeForce RTX 2080 Ti with 11 GB of VRAM evaluated the unchanged model and all five saved adapters serially. The node ran Python 3.12.10, PyTorch 2.8.0 with CUDA 12.8, Transformers 4.57.3 and PEFT 0.18.0. The evaluation used emulated BF16 on this GPU."),
  P("The queue ran overnight on 21 November 2026 from 00:35 to 06:27 Hong Kong time. The six evaluations and seven paired comparisons took 5 h 51 min 50 s of wall time and wrote 3,600 predictions with zero runtime errors. Section 5 breaks down the measured runtime and estimated cost."),

  H1("4 Results"),
  P("Table 1 gives the accuracy and output length for all six conditions. Figures 1 and 2 show how these measures change with the budget for the original-solution and English-shortest adapters. Appendices A and B give timing, failure counts, and paired estimates."),
  small("**Table 1:** Each condition used the same 200 development questions at each reasoning budget. The column numbers give budgets in tokens.", { keepNext: true, spacing: { before: 120, after: 100 } }),
  table1(),

  H2("4.1 Compact English with a tight budget"),
  P("At 128 tokens, the English-shortest adapter answered 72 of 200 questions correctly and used 53.52 mean output tokens. The original-solution adapter answered 73 correctly and used 102.56 mean tokens. That is a 47.8% reduction in output length and a −0.5 pp difference in accuracy, with a 95% interval of [−7.0, +6.5] points. The English-feedback adapter answered 71 correctly, with 57.26 mean output tokens. Both English adapters met the proposal's 20% token-reduction and at-most-three-point accuracy-loss targets on point estimates at this budget. The intervals extend below that accuracy margin, which leaves room for a meaningful loss."),
  P("At budget 128, 59 of the original-adapter outputs were truncated, compared with three for English shortest. A compact solution can fit more of the calculation into the same space. Mean generation time also fell from 8.29 to 5.22 seconds per question for this pair. Those times describe this GPU and evaluation program."),
  fig(1),
  caption("Figure 1", "Original solutions rose from 36.5% to 43.5% accuracy when the reasoning budget increased to 256 tokens. English shortest stayed at 36.0% across all three budgets."),

  H2("4.2 Original solutions with more room"),
  P("All four compact adapters kept the same total correct counts across the three budgets. Their outputs rarely reached a cap, and 196 or 197 of each adapter's 200 outputs were identical at all three budgets. The original-solution adapter rose from 73 correct at budget 128 to 87 at 256 and stayed at 87 at 512. With additional room, it produced fewer truncated outputs and answered more questions correctly. At 256 and 512 the compact adapters used 46–52% fewer output tokens than the original adapter and scored 7.5–13.0 points lower. Each of the eight corresponding paired intervals excluded zero. These comparisons hold the configured budget fixed, so the actual generation costs can differ."),
  P("The unchanged model scored below the original-solution adapter at every budget. At 256 it returned 87 unparseable answers out of 200, compared with two for the original adapter. Accuracy in this setup depends on writing an answer the parser can read in addition to solving the problem. On the seed-spacing question in Section 4.4, the unchanged model wrote the unit conversion and reached 80, and its answer line was still scored unparseable. This limits an interpretation of the full gain as an improvement in arithmetic ability alone."),
  fig(2),
  caption("Figure 2", "English shortest averaged 53.52 to 55.67 tokens across the sweep, versus 102.56 to 114.18 for original solutions. The measures count generated reasoning and answer tokens."),

  H2("4.3 What allowing Mandarin changed"),
  P("At a budget of 256, allowing Mandarin changed mean output length by less than four tokens under either selection rule. The English-shortest adapter averaged 54.40 tokens and got 72 answers right. The multilingual-shortest adapter averaged 54.78 tokens and got 61 right. The English-feedback adapter averaged 58.73 tokens and got 71 right. Its multilingual counterpart averaged 55.14 tokens and got 64 right, a 6.1% token saving with seven fewer correct answers. The gains from shortening original prose were much larger than the length changes from permitting Mandarin."),
  P("The observed accuracy differences between English and multilingual adapters were the same at all three budgets. Nearly all compact outputs are identical across budgets, so the three budgets repeat one comparison. Under shortest selection the difference was −5.5 pp with a paired interval of [−13.0, +1.5]. Under feedback it was −3.5 pp with an interval of [−10.5, +3.0]. Mean training-solution lengths also differed by less than one token between the English and multilingual pools under each selection rule. The paired intervals leave the additional effect of language choice on accuracy uncertain."),
  P("An exploratory comparison within each language pool gave −0.5 pp for feedback versus shortest in English (95% interval [−5.5, +5.0]) and +1.5 pp in the multilingual pool (interval [−4.0, +7.0]) at each budget. Both intervals include zero. The feedback probe provided a different way to pick examples, with no clear resulting gain on this development set."),
  P("Figure 3 shows the seven accuracy comparisons at budget 256. At each budget, both matching English-to-multilingual intervals cross zero."),

  H2("4.4 Language and completeness in saved outputs"),
  P("At budget 256, 193 of 200 multilingual-shortest outputs and 191 of 200 multilingual-feedback outputs contained Han characters. Both Han and Latin characters appeared in 78 and 66 outputs, respectively. The other four conditions produced zero Han-containing outputs. Latin letters can be names, variables or English words, so the character counts are a starting point for inspection. For example, a multilingual-feedback output used the English label *Jose rocks 14 fewer* before `80-14=66`, then used `Albert比Joshua多` to label `86-80=6`. The same solution uses English and Mandarin to describe two different relations."),
  fig(3),
  caption("Figure 3", "Paired accuracy differences at budget 256 with 95% bootstrap intervals. Each dot compares the same 200 questions. The shaded rows compare a compact adapter with the original-solution adapter. Appendix B gives the intervals at all three budgets."),
  P("We used an AI-assisted reading of 48 saved outputs, one per condition for each of eight questions at budget 256. The questions were selected to illustrate cases flagged by numeric coverage and language checks. The sample can show how steps change, while systematic human annotation is still pending. The examples below illustrate distinct outcomes within that sample."),
  P("**A calculation can survive compression.** For a family-reunion problem about weight gain, the original solution writes out the intermediate values 10 and 6 on separate lines. The multilingual-feedback output combined the operations into `2*5+2=12` and `12/2-3=3`, then reached the correct total of 20 in 47 tokens. English feedback wrote the same two equations and reached 20 in 59 tokens. The original adapter also reached 20 and used 146 tokens. The shorter traces keep the operations even though they omit the separate intermediate values."),
  P("**An omitted conversion can change the answer.** A problem asks how many seeds can fit in a 120-foot row with 18 inches per seed. English feedback wrote `18/12=1.5` to convert inches to feet before dividing `120/1.5=80`, using 44 tokens. Multilingual feedback wrote `120/18=6` without converting the units and returned 6 in 38 tokens. The quotient there is 6.67, so the line also rounds down. The shortest pair split the same way. English shortest converted first and answered 80 in 55 tokens, and multilingual shortest also divided 120 by 18 and answered 108 in 41. The original-solution adapter missed this question too. It tried the conversion but divided 120 by 12 where it needed to multiply, and answered 10/18 in 70 tokens. Trouble with the units was not unique to the compact adapters."),
  P("**A correct final number can hide bad steps.** On the weight-gain problem, multilingual shortest used 10 where Jose's gain should have been 12, then gave Fernando a gain of 5 instead of 3. Its final sum was still 20 because the two individual errors offset. Exact-answer accuracy credits both that trace and the complete one. This illustrates why we check the written calculations alongside the final answer."),

  H1("5 Time and cost of the pilot"),
  P("The run records give separate timings for the three core stages. Calibration scoring, the eight-attempt repeat and training-candidate scoring used 3 hours 53 minutes of recorded generation on the course GPU. The five final laptop training commands took 14 minutes 12 seconds altogether. The course development evaluation and paired comparisons took 5 hours 52 minutes of wall time. This adds up to about 10 recorded hours across the core stages, with scoring measured inside generation and training and evaluation measured by elapsed command time."),
  P("For a repeat of this pilot, the observed condition-by-budget generation means of 4.76 to 9.20 seconds per question give a planning range of about 4.8 to 9.2 hours for 3,600 outputs. Adding the logged scoring and training time gives roughly 9 to 13 compute hours, before collection, human review, setup and retries. This range brackets the workload with the fastest and slowest observed means. The finished sweep provides the more direct timing for this hardware."),
  P("Teacher rewrites used an existing subscription and the course GPU ran on the university allocation. The project log contains no separate per-token or rental invoice for this run. As a budgeting example for 200 teacher prompts, we used the worksheet's assumptions of 2,200 input and 2,000 visible output characters per question, three to four characters per token, and 1,000 to 4,000 additional output-side reasoning tokens. At the worksheet's planning rates of US$4 per million input and US$20 per million output tokens, that gives about US$6 to US$20 before retries. This is a hypothetical teacher API range. It excludes subscription fees, electricity and labour."),

  H1("6 Limitations"),
  P("The experiment used one model, 86 training questions and one training seed. The question-level intervals describe variation across development examples with the saved adapters and decoding draws. A new adaptation may change a difference measured here. The groups are disjoint within the prepared GSM8K split, while the model's pretraining data is outside our control. An independent transfer set and the official test were outside this development evaluation. The trade-offs therefore apply to this pilot."),
  P("The intervals also omit variation between decoding runs. As a quick check before the course sweep, we decoded the same six conditions on the first 50 development questions at budget 256 on the laptop RTX 4060, which runs BF16 natively. The configuration, seeds and software versions matched the course run. At most four of the 50 outputs per condition matched the course run word for word. On those 50 questions, the laptop and course runs gave 18 and 18 correct for the unchanged model, 26 and 25 for original solutions, 15 and 21 for English shortest, 21 and 21 for English feedback, 23 and 16 for multilingual shortest, and 24 and 18 for multilingual feedback. The original adapter led every compact adapter in both runs. The English-versus-multilingual direction reversed under both selection rules. The multilingual adapters were ahead on the laptop and behind on the course GPU. We did not isolate the cause. We report the course run because it covers all 200 questions and all three budgets on one GPU. A single decode cannot settle differences of a few questions."),
  P("The two language pools received different meaning reviews, and feedback was measured with only two attempts per candidate. The stability check shows that the pick can change when more completions are available. We also encountered four wrong or doubtful source answers across the 100 training and first 100 calibration questions through incidental review. Vendrow et al. document label problems in their benchmark audits [9]. The development set did not receive a systematic label audit. A paired evaluation puts the same labels in front of each condition, but a mistaken label can still reward one answer and penalize another."),
  P("Generated tokens and elapsed seconds answer related questions. The compact adapters generally produced fewer tokens and took fewer seconds than the original adapter. Timing includes both generation stages on one course GPU. Energy and speed on other hardware remain outside this measurement."),

  H1("7 Conclusion"),
  P("The clearest token saving came from short English. At the 128-token reasoning budget, the shortest-English adapter used 47.8% fewer generated tokens and got 72 of 200 questions right, compared with 73 for the original-solution adapter. Both compact English adapters met the proposal's token and accuracy targets on point estimates at that budget. The paired 95% interval for the accuracy difference, [−7.0, +6.5] percentage points, still allows a meaningful loss. With more room at 256 and 512, the original adapter reached 87 correct and shortest English stayed at 72. The compact solutions paid off at the tight budget and cost accuracy at the larger ones."),
  P("Allowing Mandarin changed what the models wrote. The multilingual adapters used Han characters in more than 95% of their outputs. The matched language comparisons showed smaller changes in output length, and both paired accuracy intervals included zero at every budget. In this pilot, shortening the training solutions had a clearer effect on token use than making a second language available. Settling the accuracy effect of the second language needs repeated decoding runs and more training seeds."),

  H1("Reproducibility"),
  P("The experiment record preserves question IDs, candidate decisions, model and dataset revisions, five saved adapters, generation config, predictions and paired comparisons."),
  new Paragraph({ spacing: { after: 0 }, children: runs("Qwen3-0.6B revision `c1899de289a04d12100db370d81485cdf75e47ca`", { size: 20 }) }),
  new Paragraph({ spacing: { after: 200 }, children: runs("GSM8K revision `740312add88f781978c0658806c59bc2815b9866`", { size: 20 }) }),

  H1("References"),
  ...REFS.map(reference),

  new Paragraph({ children: [new PageBreak()] }),
  H1("A All development measurements"),
  small("Each row contains results for 200 questions. Tokens and seconds are means per prediction. Unparseable and truncated counts can overlap. All six evaluations completed without runtime errors.", { keepNext: true }),
  tableA(),

  H1("B Planned paired comparisons"),
  small("A positive reduction means the candidate generated fewer tokens. The accuracy change is candidate minus reference, in percentage points. All intervals use the paired question bootstrap described above.", { keepNext: true }),
  tableB(),

  new Paragraph({ children: [new PageBreak()] }),
  H1("C Timing and answer format"),
  small("At budget 128, the original adapter truncated 59 of 200 outputs. This fell to two at 256 and zero at 512. The unchanged model's truncations also fell with the larger budgets, from 93 to 14 to one. Its unparseable answer count remained high at 512, with 88 of 200 answers. Truncation and parsing therefore give different information about why a prediction receives no credit."),
  fig(4),
  caption("Figure 4", "Mean generation time per question for original solutions and English shortest on the course RTX 2080 Ti.", { indent: { left: 650, right: 650 } }),
  fig(5),
  caption("Figure 5", "Outputs without a parseable final answer for unchanged Qwen and original solutions, out of 200.", { indent: { left: 650, right: 650 } }),
  fig(6),
  caption("Figure 6", "Outputs flagged for reaching the reasoning or answer cap, out of 200. Appendix A gives these diagnostics for all conditions.", { indent: { left: 650, right: 650 } }),
];

const heading = (size, before, after) => ({ run: { font: BODY, size, bold: true, color: "000000" }, paragraph: { spacing: { before, after }, keepNext: true, keepLines: true } });
const doc = new Document({
  creator: "Charles Joshua T. Uy and Wat King Ki",
  title: "Now You're Thinking My Language: Learning Compact Multilingual Reasoning Dialects for Small Language Models",
  styles: {
    default: {
      document: { run: { font: BODY, size: 22 }, paragraph: { spacing: { line: 240 } } },
      heading1: heading(29, 340, 170),
      heading2: heading(24, 260, 130),
    },
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1304, bottom: 1304, left: 1304, right: 1304 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 20 })] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(outPath, buffer);
  console.log("wrote", outPath, buffer.length);
});
