# Course paper

`build_paper.js` holds the paper text and layout. It writes `output/docx/paper.docx`. `build.ps1` runs it and then exports `output/pdf/paper.pdf` with Microsoft Word.

## Rebuild

```powershell
npm --prefix paper install
pwsh paper/build.ps1
```

Without Word, run `node paper/build_paper.js` and convert the docx with LibreOffice. Edit the text in `build_paper.js` and rebuild. Edits made directly in the docx are lost on the next build.

## Numbers

`verify_numbers.py` recomputes these from the ignored local artifacts and writes `verified.json`:

- every row of Appendix A and Appendix B, checked against the run summaries;
- correct counts on the first 50 development questions for the laptop quick decode and the course run;
- how many outputs are identical at all three budgets;
- Han-character counts at budget 256;
- token counts and correctness for the three example questions.

The build reads the table numbers from `verified.json`. Raw model outputs stay in `artifacts/`. Rerun the script only on a machine that holds `artifacts/handoff/2026-11-21-opus55-aiassist-school-results/` and the six `artifacts/runs/opus55-aiassist-laptop-*-quick/` runs.

```powershell
.venv\Scripts\python.exe paper\verify_numbers.py
uv run --no-project --with matplotlib python paper\figure3.py
```

## Figures

`figure3.py` draws Figure 3 from `verified.json`. Figures 1, 2, 4, 5 and 6 are 360 dpi crops of the 21 November 2026 paper PDF, because the plotting source for that version is not in this repository. `figures/sizes.json` gives each figure's placed size in points.

## Labels to keep

The paper reports a development pilot with one training seed and one decoding run. The official test was not run. In each multilingual condition, 76 of the 86 training rewrites were approved only by an AI reviewer. Keep these labels when editing the text.
