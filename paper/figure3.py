"""Draw Figure 3 from the paired comparisons in verified.json.

Usage: uv run --no-project --with matplotlib python paper/figure3.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
verified, out_png = HERE / "verified.json", HERE / "figures" / "figure3.png"
rows = [r for r in json.load(open(verified, encoding="utf-8"))["appendix_b"] if r[0] == 256]
by_pair = {(r[1], r[2]): r for r in rows}
ORDER = [
    ("unchanged", "original", "Unchanged → original"),
    ("original", "english-shortest", "Original → English shortest"),
    ("original", "english-feedback", "Original → English feedback"),
    ("original", "multilingual-shortest", "Original → multilingual shortest"),
    ("original", "multilingual-feedback", "Original → multilingual feedback"),
    ("english-shortest", "multilingual-shortest", "English → multilingual (shortest)"),
    ("english-feedback", "multilingual-feedback", "English → multilingual (feedback)"),
]
INK, TEXT, GRID, BAND = "#18273a", "#4d5b66", "#d5dcdc", "#eef6f5"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.4})
fig, ax = plt.subplots(figsize=(6.45, 2.95))
ys = list(range(len(ORDER)))[::-1]
ax.axhspan(ys[4] - 0.5, ys[1] + 0.5, color=BAND, zorder=0)
for x in (-20, -10, 10, 20):
    ax.axvline(x, color=GRID, linewidth=0.9, zorder=1)
ax.axvline(0, color=TEXT, linewidth=1.3, linestyle=(0, (3, 2)), zorder=2)
for y, (ref, cand, _label) in zip(ys, ORDER):
    _b, _r, _c, diff, lo, hi, *_ = by_pair[(ref, cand)]
    ax.plot([lo, hi], [y, y], color=INK, linewidth=1.6, zorder=3)
    for end in (lo, hi):
        ax.plot([end, end], [y - 0.09, y + 0.09], color=INK, linewidth=1.6, zorder=3)
    ax.plot(diff, y, "o", color=INK, markersize=5.5, zorder=4)
ax.set_yticks(ys)
ax.set_yticklabels([label for _r, _c, label in ORDER], color=TEXT)
ax.set_xticks([-20, -10, 0, 10, 20])
ax.set_xticklabels(["−20", "−10", "0", "10", "20"], color=TEXT)
ax.set_xlim(-24, 26)
ax.set_ylim(-0.6, len(ORDER) - 0.4)
ax.tick_params(length=0, pad=6)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.set_xlabel("Accuracy change, candidate minus reference (percentage points)", color=TEXT, labelpad=6, loc="right")
ax.set_title("256-token reasoning budget", loc="left", color=INK, fontweight="bold", fontsize=10.5, pad=8)
fig.tight_layout(pad=0.4)
fig.savefig(out_png, dpi=400)
print("saved", out_png, fig.get_size_inches())
