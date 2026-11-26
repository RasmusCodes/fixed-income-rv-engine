"""PCA of curve movements per market: shares of variance, loadings, stability across
regimes and rolling windows, and decomposition of the largest historical moves.

Episodes are not hand-picked: for each market the three largest non-overlapping
63-observation moves in the level (PC1) and slope (PC2) factors are found from the data,
then decomposed into level, slope, curvature and a residual.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .. import market as M
from ..curves.pca import decompose_move, loading_stability, pca_changes
from .common import REGIMES

PCA_TENORS = {
    "US": (1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0),
    "DE": (1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0),
    "FR": (1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0),
    "UK": (1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0),
    "JP": (1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0),
    "PL": (1.0, 2.0, 3.0, 5.0, 7.0, 10.0),
}


def levels(market: str, start="2000-01-01") -> pd.DataFrame:
    """Par yields at the PCA tenors. Incomplete rows are KEPT (as NaN) so that changes are
    never taken across a gap in the data."""
    p = M.cm_panel(market)
    cols = [t for t in PCA_TENORS[market] if t in p.columns]
    out = p[cols].dropna(how="all")
    return out[out.index >= pd.Timestamp(start)]


def full_and_regimes(market: str, k: int = 3) -> tuple[dict, pd.DataFrame]:
    lv = levels(market)
    full = pca_changes(lv, k)
    rows = []
    for name, a, b in [("all (2000-)", None, None)] + REGIMES:
        sub = lv
        if a:
            sub = sub[sub.index >= pd.Timestamp(a)]
        if b:
            sub = sub[sub.index <= pd.Timestamp(b)]
        if len(sub) < 60:
            continue
        try:
            r = pca_changes(sub, k)
        except ValueError:          # e.g. UK before 2016: no 30y point, so no complete rows
            continue
        row = {"market": market, "regime": name, "n": r.n_obs}
        for i in range(k):
            row[f"expl_PC{i + 1}"] = r.explained[i]
            row[f"vol_PC{i + 1}_bp"] = float(np.sqrt(r.eigenvalues[i]))
            row[f"cos_PC{i + 1}"] = float(abs(r.loadings[:, i] @ full.loadings[:, i]))
        rows.append(row)
    return {"pca": full, "levels": lv}, pd.DataFrame(rows)


def episodes(market: str, pca, lv: pd.DataFrame, days: int = 91, top: int = 3) -> list[dict]:
    """Largest non-overlapping moves in PC1 and PC2 over about three calendar months
    (``days``), whatever the data frequency."""
    sc = pca.scores
    complete = lv.dropna(how="any")
    spacing = float(np.median(np.diff(sc.index.values).astype("timedelta64[D]").astype(float)))
    window = max(4, int(round(days / max(spacing, 1.0) * (5 / 7 if spacing < 2 else 1))))
    out = []
    for comp in ("PC1", "PC2"):
        roll = sc[comp].rolling(window).sum().dropna()
        taken = []
        for end, val in roll.abs().sort_values(ascending=False).items():
            i = sc.index.get_loc(end)
            start = sc.index[i - window + 1]
            if (end - start).days > 1.5 * days:          # window spans a data gap
                continue
            if any(abs(i - j) < window for j in taken):
                continue
            prior = complete.index[complete.index < start]
            if not len(prior) or end not in complete.index:
                continue
            taken.append(i)
            d0 = prior[-1]
            dec = decompose_move(complete, d0, end, pca)
            out.append({"market": market, "factor": comp, "start": d0, "end": end,
                        "change_bp": {float(k): round(float(v), 1) for k, v in zip(dec["tenors"], dec["change"])},
                        "pc_scores_bp": np.round(dec["scores"], 1).tolist(),
                        "residual_rms_bp": float(np.sqrt(np.mean(dec["residual"] ** 2)))})
            if len(taken) >= top:
                break
    return out


def run(markets=("US", "DE", "FR", "UK", "JP", "PL")):
    tables, stab, eps, loadings = [], [], [], {}
    for m in markets:
        try:
            res, tab = full_and_regimes(m)
        except Exception as exc:  # e.g. Poland before its curves are built
            print(f"  PCA {m} skipped: {exc}")
            continue
        tables.append(tab)
        st = loading_stability(res["levels"], window="730D", step="182D")
        st.insert(0, "market", m)
        stab.append(st)
        eps += episodes(m, res["pca"], res["levels"])
        p = res["pca"]
        loadings[m] = {"tenors": p.tenors.tolist(), "loadings": p.loadings.tolist(),
                       "explained": p.explained.tolist(), "vol_bp": np.sqrt(p.eigenvalues).tolist(),
                       "start": str(p.start.date()), "end": str(p.end.date()), "n": p.n_obs}
    return (pd.concat(tables, ignore_index=True), pd.concat(stab, ignore_index=True),
            pd.DataFrame(eps), loadings)
