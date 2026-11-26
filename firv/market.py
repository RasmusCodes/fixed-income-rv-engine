"""Country curve configuration and a uniform way to get curves for any date.

Each market has one primary source (see :mod:`firv.data.sources`) and a coupon convention
used whenever par yields are compared across countries:

    US  Treasury par yields (CMT)           par, semiannual      official
    DE  Bundesbank Svensson zero curve      zero, continuous     official estimate
    FR  Banque de France TEC                par, annual          official (Euronext index)
    PL  BondSpot fixing -> NSS (this repo)  bonds, annual        official fixing, derived fit
    UK  Bank of England nominal spot curve  zero, continuous     official estimate
    JP  MoF JGB constant-maturity yields    par, semiannual      official
    EA  ECB AAA Svensson curve              params, continuous   official estimate

``cm_panel(country)`` returns constant-maturity par yields (percent, the country's own
coupon frequency) on a common tenor grid; all cross-country analytics use it.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pandas as pd

from .curves import CurveData, Svensson, ZeroCurve, fit
from .data.loaders import Panel

STD_TENORS = (1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0)


@dataclass(frozen=True)
class Market:
    code: str
    name: str
    currency: str
    panel: str
    kind: str              # par | zero | params
    freq: int              # coupon frequency of local government bonds
    funding: str           # short-rate proxy description
    source: str
    max_tenor: float = 30.0
    frequency: str = "daily"


MARKETS = {
    "US": Market("US", "United States", "USD", "us_par", "par", 2, "SOFR (NY Fed)", "ust_par"),
    "DE": Market("DE", "Germany", "EUR", "de_zero", "zero", 1, "EUR STR (ECB)", "bbk_svensson"),
    "FR": Market("FR", "France", "EUR", "fr_tec", "par", 1, "EUR STR (ECB)", "bdf_tec"),
    "PL": Market("PL", "Poland", "PLN", "pl_par", "par", 1, "NBP reference rate (BIS)", "bondspot_fixing",
                 max_tenor=20.0, frequency="weekly"),
    "UK": Market("UK", "United Kingdom", "GBP", "uk_nominal", "zero", 2, "Bank Rate (BIS)", "boe_glc",
                 max_tenor=40.0),
    "JP": Market("JP", "Japan", "JPY", "jp_par", "par", 2, "BoJ policy rate (BIS)", "mof_jgb", max_tenor=40.0),
}


@lru_cache(maxsize=32)
def panel(name: str) -> Panel:
    return Panel.load(name)


def observations(country: str, date) -> CurveData:
    """Market observations for one date as CurveData (decimals)."""
    m = MARKETS[country]
    df = panel(m.panel).data
    row = df.loc[pd.Timestamp(date)].dropna()
    t = np.array([float(c) for c in row.index])
    y = row.to_numpy(float) / 100.0
    keep = t <= m.max_tenor + 1e-9
    t, y = t[keep], y[keep]
    if m.kind == "zero":
        return CurveData(t, y, kind="zero")
    return CurveData(t, y, kind="par", freq=m.freq)


def nearest_date(country: str, date) -> pd.Timestamp:
    df = panel(MARKETS[country].panel).data.dropna(how="all")
    idx = df.index[df.index <= pd.Timestamp(date)]
    return idx[-1]


def curve_on(country: str, date, method: str = "nss"):
    """Fitted curve (FitResult) for a country and date (latest earlier date if needed)."""
    d = nearest_date(country, date)
    return fit(method, observations(country, d))


def _par_from_zero_rows(df: pd.DataFrame, tenors, freq: int) -> pd.DataFrame:
    """Par yields (%) from rows of continuously compounded zero rates (%)."""
    cols = np.array([float(c) for c in df.columns])
    out = np.full((len(df), len(tenors)), np.nan)
    vals = df.to_numpy(float) / 100.0
    for i in range(len(df)):
        ok = ~np.isnan(vals[i])
        if ok.sum() < 4:
            continue
        c = ZeroCurve(cols[ok], vals[i, ok], interp="linear")
        tmax = cols[ok].max()
        for j, T in enumerate(tenors):
            if T <= tmax + 1e-9:
                out[i, j] = c.par_yield(float(T), freq) * 100
    return pd.DataFrame(out, index=df.index, columns=[float(t) for t in tenors])


@lru_cache(maxsize=16)
def cm_panel(country: str, tenors=STD_TENORS) -> pd.DataFrame:
    """Constant-maturity par yields (%) at standard tenors in the country's convention.

    Par-yield sources are used as published at the tenors they publish (missing tenors are
    left NaN rather than invented); zero-curve sources are converted to par yields (cached
    in data/processed/cm_<country>.parquet)."""
    from .data.http import PROCESSED
    m = MARKETS[country]
    src = PROCESSED / f"{m.panel}.parquet"
    cache = PROCESSED / f"cm_{country}.parquet"
    if m.kind == "zero" and cache.exists() and cache.stat().st_mtime >= src.stat().st_mtime \
            and tuple(tenors) == STD_TENORS:
        out = pd.read_parquet(cache)
        out.columns = [float(c) for c in out.columns]
        return out
    df = panel(m.panel).data
    if m.kind == "zero":
        out = _par_from_zero_rows(df, tenors, m.freq)
    else:
        out = pd.DataFrame(index=df.index, columns=[float(t) for t in tenors], dtype=float)
        for T in tenors:
            if float(T) in df.columns:
                out[float(T)] = df[float(T)]
    out = out.dropna(how="all")
    out = out.loc[:, out.notna().any()]
    if m.kind == "zero" and tuple(tenors) == STD_TENORS:
        o = out.copy()
        o.columns = [str(c) for c in o.columns]
        o.to_parquet(cache)
    return out


def zero_panel(country: str, tenors=STD_TENORS) -> pd.DataFrame:
    """Continuously compounded zero rates (%) at standard tenors: published zero curves
    directly, par-yield sources by bootstrapping each day."""
    from .curves import bootstrap_par
    m = MARKETS[country]
    df = panel(m.panel).data
    if m.kind == "zero":
        cols = np.array([float(c) for c in df.columns])
        out = {}
        for T in tenors:
            j = np.argmin(np.abs(cols - T))
            if abs(cols[j] - T) < 1e-6:
                out[float(T)] = df.iloc[:, j]
        return pd.DataFrame(out).dropna(how="all")
    rows, idx = [], []
    cols = np.array([float(c) for c in df.columns])
    for d, r in df.iterrows():
        v = r.to_numpy(float) / 100.0
        ok = ~np.isnan(v) & (cols <= m.max_tenor + 1e-9)
        if ok.sum() < 4:
            continue
        c = bootstrap_par(cols[ok], v[ok], m.freq)
        tmax = cols[ok].max()
        rows.append([float(c.zero(T)) * 100 if T <= tmax + 1e-9 else np.nan for T in tenors])
        idx.append(d)
    return pd.DataFrame(rows, index=pd.DatetimeIndex(idx), columns=[float(t) for t in tenors])


def funding_rate(country: str) -> pd.Series:
    """Daily short-rate series (%) used to finance positions (forward filled)."""
    if country == "US":
        s = panel("us_sofr").data["SOFR"].dropna()
        # before SOFR (April 2018) the 3-month T-bill CMT; after its start, SOFR only
        bill = panel("us_par").data[0.25].dropna()
        s = pd.concat([bill[bill.index < s.index[0]], s])
    elif country in ("DE", "FR"):
        s = panel("ea_estr").data["ESTR"].dropna()
        # before EUR STR (Oct 2019) the 6-month Bund zero rate as the GC funding proxy
        b = panel("de_zero").data[0.5].dropna()
        s = pd.concat([b[b.index < s.index[0]], s])
    elif country == "PL":
        s = panel("policy_rates").data["PL"]
    elif country == "UK":
        s = panel("policy_rates").data["UK"]
    elif country == "JP":
        s = panel("policy_rates").data["JP"]
    else:
        raise KeyError(country)
    return s.sort_index().ffill()


def svensson_from_row(row) -> Svensson:
    return Svensson(row["BETA0"] / 100, row["BETA1"] / 100, row["BETA2"] / 100, row["BETA3"] / 100,
                    row["TAU1"], row["TAU2"])
