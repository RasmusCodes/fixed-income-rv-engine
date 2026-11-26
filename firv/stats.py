"""Small statistics toolkit: z-scores, mean-reversion half-life, Newey-West t-statistics,
performance summaries."""
from __future__ import annotations

import numpy as np
import pandas as pd


def zscore(x: pd.Series, window: int, min_periods: int | None = None) -> pd.Series:
    """Rolling z-score using information up to and including each date (no look-ahead)."""
    mp = min_periods or max(window // 2, 10)
    m = x.rolling(window, min_periods=mp).mean()
    s = x.rolling(window, min_periods=mp).std()
    return (x - m) / s


def half_life(x: pd.Series) -> float:
    """Half-life (in observations) of an AR(1) fitted to x: dx_t = a + b x_{t-1} + e."""
    s = x.dropna()
    if len(s) < 20:
        return np.nan
    y = s.diff().iloc[1:].to_numpy()
    X = s.shift(1).iloc[1:].to_numpy()
    A = np.column_stack([np.ones_like(X), X])
    b = np.linalg.lstsq(A, y, rcond=None)[0][1]
    return float(-np.log(2) / np.log1p(b)) if -1 < b < 0 else np.inf


def newey_west_t(x, lags: int = 10) -> float:
    """t-statistic of the mean with Newey-West (Bartlett) HAC standard errors."""
    v = np.asarray(pd.Series(x).dropna(), float)
    n = len(v)
    if n < lags + 5:
        return np.nan
    e = v - v.mean()
    s = e @ e / n
    for k in range(1, lags + 1):
        w = 1 - k / (lags + 1)
        s += 2 * w * (e[k:] @ e[:-k]) / n
    se = np.sqrt(s / n)
    return float(v.mean() / se) if se > 0 else np.nan


def max_drawdown(cum: pd.Series) -> float:
    c = pd.Series(cum).dropna()
    return float((c - c.cummax()).min()) if len(c) else np.nan


def summarize(pnl: pd.Series, periods_per_year: float, position: pd.Series | None = None,
              costs: pd.Series | None = None, nw_lags: int | None = None) -> dict:
    """Performance of a P&L series in bp per unit of DV01 (per period)."""
    p = pnl.dropna()
    if len(p) < 10:
        return {"n": len(p)}
    mu, sd = p.mean(), p.std()
    lags = nw_lags if nw_lags is not None else int(round(periods_per_year / 25)) or 2
    out = {
        "start": p.index[0], "end": p.index[-1], "n": len(p),
        "ann_return_bp": mu * periods_per_year,
        "ann_vol_bp": sd * np.sqrt(periods_per_year),
        "sharpe": (mu / sd * np.sqrt(periods_per_year)) if sd > 0 else np.nan,
        "t_nw": newey_west_t(p, lags),
        "max_dd_bp": max_drawdown(p.cumsum()),
        "hit_rate": float((p[p != 0] > 0).mean()) if (p != 0).any() else np.nan,
    }
    if position is not None:
        pos = position.reindex(p.index).fillna(0.0)
        out["time_in_market"] = float((pos.abs() > 1e-9).mean())
        out["turnover_per_year"] = float(pos.diff().abs().sum() / max(len(p), 1) * periods_per_year)
    if costs is not None:
        out["cost_bp_per_year"] = float(costs.reindex(p.index).fillna(0).sum() / len(p) * periods_per_year)
    return out
