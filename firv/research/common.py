"""Shared data assembly for research scripts: yield series by name, funding rates,
roll-down slopes and backtest inputs."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

from .. import market as M
from ..backtest import Inputs, Leg
from ..data.loaders import Panel

SERIES_FREQ = {"US": 2, "DE": 1, "FR": 1, "PL": 1, "UK": 2, "JP": 2,
               "US_SWAP": 2, "UK_OIS": 1, "US_REAL": 2, "UK_REAL": 2, "US_BAA": 2, "US_AAA": 2}
REGIMES = [("pre-2008", None, "2007-12-31"),
           ("2008-14 crisis and QE", "2008-01-01", "2014-12-31"),
           ("2015-21 low and negative rates", "2015-01-01", "2021-12-31"),
           ("2022-26 inflation and tightening", "2022-01-01", None)]


def regime_of(ts: pd.Timestamp) -> str:
    for name, a, b in REGIMES:
        if (a is None or ts >= pd.Timestamp(a)) and (b is None or ts <= pd.Timestamp(b)):
            return name
    return "other"


def _zero_to_par(name: str, tenors, freq) -> pd.DataFrame:
    df = Panel.load(name).data
    return M._par_from_zero_rows(df, tenors, freq)


@lru_cache(maxsize=32)
def series(name: str) -> pd.DataFrame:
    """Par yields (%) by tenor for a named series."""
    from ..data.http import PROCESSED
    if name in M.MARKETS:
        return M.cm_panel(name)
    cache = PROCESSED / f"series_{name}.parquet"
    if name == "US_SWAP":
        return Panel.load("us_swaps_ice").data
    if name == "US_REAL":
        return Panel.load("us_real").data
    if name in ("US_BAA", "US_AAA"):
        # Moody's seasoned long corporate yields: bonds of 20+ years, treated as a 20y point
        col = "DBAA" if name == "US_BAA" else "DAAA"
        return Panel.load("us_moodys").data[[col]].rename(columns={col: 20.0}).dropna()
    src = {"UK_OIS": "uk_ois", "UK_REAL": "uk_real"}[name]
    if cache.exists() and cache.stat().st_mtime >= (PROCESSED / f"{src}.parquet").stat().st_mtime:
        out = pd.read_parquet(cache)
        out.columns = [float(c) for c in out.columns]
        return out
    tenors = (2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0) if name == "UK_REAL" else (1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0)
    out = _zero_to_par(src, tenors, SERIES_FREQ[name]).dropna(how="all")
    out = out.loc[:, out.notna().any()]
    o = out.copy()
    o.columns = [str(c) for c in o.columns]
    o.to_parquet(cache)
    return out


def slope_at(panel: pd.DataFrame, tenor: float) -> pd.Series:
    """Roll-down slope (% per year of maturity) at ``tenor``: secant to the next shorter
    published tenor (or the next longer one at the short end)."""
    cols = sorted(float(c) for c in panel.columns)
    if len(cols) == 1:            # a single point (e.g. Moody's index): no curve to roll down
        return panel[float(tenor)] * 0.0
    i = cols.index(float(tenor))
    if i > 0:
        lo = cols[i - 1]
        return (panel[float(tenor)] - panel[lo]) / (float(tenor) - lo)
    hi = cols[i + 1]
    return (panel[hi] - panel[float(tenor)]) / (hi - float(tenor))


@lru_cache(maxsize=16)
def cpi_yoy(country: str) -> pd.Series:
    cpi = Panel.load("cpi_yoy").data[country]
    # CPI for month m is known roughly two weeks into month m+1: lag by one month end
    s = cpi.shift(1).dropna()
    return s


def funding(name: str) -> pd.Series:
    base = name.split("_")[0]
    r = M.funding_rate(base)
    if name.endswith("_REAL"):
        pi = cpi_yoy(base).reindex(r.index, method="ffill")
        return (r - pi).dropna()
    return r


def build_inputs(legs: list[Leg], start=None, end=None) -> Inputs:
    ys, fs, ss = {}, {}, {}
    for j, l in enumerate(legs):
        p = series(l.series)
        col = f"{l.series}_{l.tenor:g}_{j}"
        ys[col] = p[float(l.tenor)]
        ss[col] = slope_at(p, l.tenor)
        fs[col] = funding(l.series)
    Y = pd.DataFrame(ys).dropna()
    if start is not None:
        Y = Y[Y.index >= pd.Timestamp(start)]
    if end is not None:
        Y = Y[Y.index <= pd.Timestamp(end)]
    S = pd.DataFrame(ss).reindex(Y.index)
    Fd = pd.DataFrame({k: v.reindex(Y.index, method="ffill") for k, v in fs.items()})
    ok = S.notna().all(axis=1) & Fd.notna().all(axis=1)
    return Inputs(Y[ok], Fd[ok], S[ok], {"legs": legs})


def leg(series_name: str, tenor: float, weight: float) -> Leg:
    return Leg(series_name, float(tenor), float(weight), SERIES_FREQ[series_name])
