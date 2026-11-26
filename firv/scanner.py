"""Relative-value scanner: where does each curve point, spread and butterfly stand today
against its own history, what does it earn in carry and roll-down, and how volatile is it?

Every row is a DV01-weighted trade expressed as a spread X (bp) that the trade gains from
when X rises: for a 2s10s steepener X = 10y - 2y; for a long-belly fly X = wings - belly
... in general X = -sum_i w_i y_i. Columns:

  level_bp        current X
  z_1y, z_3y      (X - mean) / sd over the trailing 1 and 3 years (weekly sampling)
  pct_5y          percentile of today's X within the last 5 years
  chg_3m_bp       change of X over 3 months
  carry_roll_3m   expected P&L over 3 months if curves do not move (bp per DV01 unit)
  vol_ann_bp      annualised volatility of X (last year of daily changes)
  carry_to_vol    carry_roll_3m * 4 / vol_ann_bp
  half_life_w     mean-reversion half-life (weeks, AR(1) on 3 years of weekly data)
  pca_resid_bp    for single tenors: today's yield minus its 3-factor PCA fit (2y levels)

The scanner reports measurements. The ``mr_side`` column only states which side a pure
mean-reversion rule would take; the backtests in research/ show how such rules fared.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import market as M
from .backtest import Spec, _prep
from .research.common import build_inputs, leg, series
from .stats import half_life


def _spread_rows(name, family, legs, market_label):
    inp = build_inputs(legs)
    if len(inp.yields) < 60:
        return None
    Y = inp.yields
    w = np.array([l.weight for l in legs])
    X = -(Y.to_numpy() @ w) * 100.0
    Xs = pd.Series(X, index=Y.index)
    wk = Xs.groupby(pd.Grouper(freq="W-FRI")).last().dropna()
    last = wk.index[-1]

    def z(years):
        h = wk[wk.index > last - pd.DateOffset(years=years)]
        return float((h.iloc[-1] - h.iloc[:-1].mean()) / h.iloc[:-1].std()) if len(h) > 20 else np.nan

    h5 = wk[wk.index > last - pd.DateOffset(years=5)]
    pr = _prep(Spec(name, legs), inp)
    cr = float(np.nansum(w * (pr["carry"][-1] + pr["roll"][-1]))) * 91.0
    daily = Xs.diff().dropna()
    daily = daily[daily.index > Xs.index[-1] - pd.DateOffset(years=1)]
    ppy = len(daily) / 1.0 if len(daily) else 252
    vol = float(daily.std() * np.sqrt(ppy)) if len(daily) > 10 else np.nan
    hl = half_life(wk[wk.index > last - pd.DateOffset(years=3)])
    chg = Xs.iloc[-1] - Xs[Xs.index <= Xs.index[-1] - pd.DateOffset(months=3)].iloc[-1] \
        if (Xs.index <= Xs.index[-1] - pd.DateOffset(months=3)).any() else np.nan
    z1 = z(1)
    return {"market": market_label, "family": family, "trade": name, "asof": Xs.index[-1].date(),
            "level_bp": float(Xs.iloc[-1]), "z_1y": z1, "z_3y": z(3),
            "pct_5y": float((h5 < h5.iloc[-1]).mean() * 100) if len(h5) > 20 else np.nan,
            "chg_3m_bp": float(chg), "carry_roll_3m": cr, "vol_ann_bp": vol,
            "carry_to_vol": cr * 4 / vol if vol and vol > 0 else np.nan,
            "half_life_w": hl,
            "mr_side": ("sell X (reverse the trade)" if z1 > 0 else "buy X (the trade as named)") if np.isfinite(z1) else ""}


def curve_rows(m: str) -> list[dict]:
    defs = [
        ("curve", "2s10s steepener", [leg(m, 2, 1), leg(m, 10, -1)]),
        ("curve", "2s5s steepener", [leg(m, 2, 1), leg(m, 5, -1)]),
        ("butterfly", "2s5s10s fly, long belly (50/50)", [leg(m, 5, 1), leg(m, 2, -0.5), leg(m, 10, -0.5)]),
    ]
    if m == "PL":       # the Polish fixing stops at about 10 years
        defs.append(("curve", "5s10s steepener", [leg(m, 5, 1), leg(m, 10, -1)]))
    else:
        defs += [
            ("curve", "5s30s steepener", [leg(m, 5, 1), leg(m, 30, -1)]),
            ("curve", "10s30s steepener", [leg(m, 10, 1), leg(m, 30, -1)]),
            ("butterfly", "5s10s30s fly, long belly (50/50)",
             [leg(m, 10, 1), leg(m, 5, -0.5), leg(m, 30, -0.5)]),
        ]
    out = []
    for fam, name, legs in defs:
        try:
            r = _spread_rows(f"{m} {name}", fam, legs, m)
        except Exception:
            r = None
        if r:
            out.append(r)
    return out


def pca_residuals(m: str, years: int = 2, k: int = 3) -> pd.DataFrame:
    """Rich/cheap by tenor: today's yield minus its fit from the first k principal
    components of the last ``years`` of yield LEVELS (positive = cheap, yield too high)."""
    p = M.cm_panel(m).dropna()
    p = p[p.index > p.index[-1] - pd.DateOffset(years=years)]
    X = p.to_numpy() * 100.0
    mu = X.mean(axis=0)
    U, S, Vt = np.linalg.svd(X - mu, full_matrices=False)
    fit = mu + (X - mu) @ Vt[:k].T @ Vt[:k]
    resid = X - fit
    z = (resid[-1] - resid.mean(axis=0)) / resid.std(axis=0)
    return pd.DataFrame({"market": m, "tenor": [float(c) for c in p.columns],
                         "yield_pct": p.iloc[-1].to_numpy(), "pca_resid_bp": resid[-1], "resid_z": z,
                         "asof": p.index[-1].date()})


def cross_rows() -> list[dict]:
    pairs = [("FR", "DE"), ("PL", "DE"), ("PL", "FR"), ("UK", "DE"), ("US", "DE"), ("JP", "US"),
             ("FR", "DE", 2.0), ("PL", "FR", 2.0), ("PL", "FR", 5.0), ("FR", "DE", 30.0)]
    out = []
    for p in pairs:
        a, b = p[0], p[1]
        t = p[2] if len(p) > 2 else 10.0
        try:
            r = _spread_rows(f"{a} {t:g}y vs {b} {t:g}y (long {a})", "cross-country",
                             [leg(a, t, 1), leg(b, t, -1)], f"{a}-{b}")
        except Exception:
            r = None
        if r:
            out.append(r)
    for name, legs, lab in [
        ("UK 10y OIS spread (long gilt, pay OIS)", [leg("UK", 10, 1), leg("UK_OIS", 10, -1)], "UK"),
        ("US 10y breakeven (long TIPS)", [leg("US_REAL", 10, 1), leg("US", 10, -1)], "US"),
        ("UK 10y breakeven (long linker)", [leg("UK_REAL", 10, 1), leg("UK", 10, -1)], "UK"),
        ("US Baa vs 20y UST (long credit)", [leg("US_BAA", 20, 1), leg("US", 20, -1)], "US"),
    ]:
        try:
            r = _spread_rows(name, "swap/inflation/credit", legs, lab)
        except Exception:
            r = None
        if r:
            out.append(r)
    return out


def scan(markets=("US", "DE", "FR", "UK", "JP", "PL")) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for m in markets:
        rows += curve_rows(m)
    rows += cross_rows()
    table = pd.DataFrame(rows)
    table["abs_z_1y"] = table["z_1y"].abs()
    table = table.sort_values("abs_z_1y", ascending=False).drop(columns="abs_z_1y")
    res = pd.concat([pca_residuals(m) for m in markets], ignore_index=True)
    return table, res
