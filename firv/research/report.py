"""Markdown tables and a consistent chart style for the research reports."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research"
FIG = OUT / "figures"

# Reference categorical palette (light mode), fixed slot order
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, INK2, MUTED, GRID, AXIS, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"


def fmt(v, nd=2):
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return ""
    if isinstance(v, (float, np.floating)):
        return f"{v:,.{nd}f}"
    if isinstance(v, pd.Timestamp):
        return v.strftime("%Y-%m-%d")
    return str(v)


def md_table(df: pd.DataFrame, nd=2, cols=None, rename=None, max_rows=None) -> str:
    d = df[cols] if cols else df
    if max_rows:
        d = d.head(max_rows)
    names = [rename.get(c, c) if rename else c for c in d.columns]
    lines = ["| " + " | ".join(map(str, names)) + " |",
             "|" + "|".join("---:" if pd.api.types.is_numeric_dtype(d[c]) else "---" for c in d.columns) + "|"]
    for _, r in d.iterrows():
        lines.append("| " + " | ".join(fmt(v, nd) for v in r.to_numpy()) + " |")
    return "\n".join(lines)


def setup_mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
        "axes.spines.right": False, "axes.prop_cycle": matplotlib.cycler(color=SERIES),
        "lines.linewidth": 1.6, "font.size": 9, "axes.titlesize": 10, "axes.titleweight": "bold",
        "axes.titlecolor": INK, "legend.frameon": False, "text.parse_math": False,
        "font.family": ["Segoe UI", "DejaVu Sans"],
    })
    return plt


def save(fig, name: str) -> str:
    FIG.mkdir(parents=True, exist_ok=True)
    path = FIG / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(fig)
    return f"figures/{name}.png"
