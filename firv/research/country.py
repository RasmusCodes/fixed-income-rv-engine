"""Cross-country comparison: curves, market-implied policy paths, inflation, real yields,
fiscal position, sovereign spreads, volatility and FX-hedged yields.

All yields are par yields in each market's own coupon convention (see firv.market).
Implied short-rate paths are simple 1-year forward rates from the bootstrapped zero curve
(1y1y = the 1-year rate one year ahead); they include term premia, so they are not pure
expectations. FX-hedged yields use covered interest parity with policy/overnight rates
as the short-rate proxy: hedged yield = local yield - (local short rate - base short rate).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .. import market as M
from ..curves import bootstrap_par
from ..data.loaders import Panel
from .common import series

POLICY_COL = {"US": "US", "DE": "EA", "FR": "EA", "PL": "PL", "UK": "UK", "JP": "JP"}
FX_CCY = {"US": "USD", "PL": "PLN", "UK": "GBP", "JP": "JPY"}


def forwards_on(market: str, date=None) -> dict:
    p = M.cm_panel(market)
    row = p.loc[:date].dropna(how="all").iloc[-1] if date is not None else p.dropna(how="all").iloc[-1]
    row = row.dropna()
    t = np.array([float(c) for c in row.index])
    curve = bootstrap_par(t, row.to_numpy(float) / 100.0, M.MARKETS[market].freq)
    f = lambda a, b: float(curve.forward_simple(a, b)) * 100.0
    return {"1y": f(0.0, 1.0), "1y1y": f(1.0, 2.0), "2y1y": f(2.0, 3.0), "5y5y": f(5.0, 10.0)}


def latest(df: pd.DataFrame, col, asof=None):
    s = df[col].dropna()
    if asof is not None:
        s = s[s.index <= pd.Timestamp(asof)]
    return (float(s.iloc[-1]), s.index[-1]) if len(s) else (np.nan, None)


def snapshot(markets=("US", "DE", "FR", "UK", "JP", "PL"), asof=None) -> pd.DataFrame:
    pol = Panel.load("policy_rates").data
    cpi = Panel.load("cpi_yoy").data
    fis = Panel.load("oecd_fiscal").data
    rows = []
    de = M.cm_panel("DE")
    us = M.cm_panel("US")
    for m in markets:
        p = M.cm_panel(m)
        if asof is not None:
            p = p[p.index <= pd.Timestamp(asof)]
        last = p.dropna(how="all").iloc[-1]
        d = p.dropna(how="all").index[-1]
        long_end = 10.0 if m == "PL" else 30.0
        r = {"market": m, "name": M.MARKETS[m].name, "currency": M.MARKETS[m].currency, "asof": d.date()}
        for T in (2.0, 5.0, 10.0, 30.0):
            r[f"y{T:g}"] = float(last.get(T, np.nan))
        r["slope_2s10s_bp"] = (r["y10"] - r["y2"]) * 100
        r["slope_5s_long_bp"] = (float(last.get(long_end, np.nan)) - r["y5"]) * 100
        r["long_end"] = long_end
        pv, pd_ = latest(pol, POLICY_COL[m], d)
        r["policy_rate"] = pv
        fw = forwards_on(m, d)
        r.update({f"fwd_{k}": v for k, v in fw.items()})
        r["implied_1y_change_bp"] = (fw["1y1y"] - fw["1y"]) * 100
        cv, cd = latest(cpi, m)
        r["cpi_yoy"] = cv
        r["cpi_month"] = cd.strftime("%Y-%m") if cd is not None else ""
        r["real_10y_expost"] = r["y10"] - cv if np.isfinite(cv) else np.nan
        if m == "US":
            rr = series("US_REAL")
            r["real_10y_market"] = float(rr[10.0].dropna().loc[:d].iloc[-1])
        elif m == "UK":
            rr = series("UK_REAL")
            r["real_10y_market"] = float(rr[10.0].dropna().loc[:d].iloc[-1])
        else:
            r["real_10y_market"] = np.nan
        r["breakeven_10y"] = r["y10"] - r["real_10y_market"] if np.isfinite(r["real_10y_market"]) else np.nan
        year = d.year
        for key, col in (("debt_gdp", f"{m}_GGFLQ"), ("deficit_gdp", f"{m}_NLGQ")):
            if col in fis.columns:
                s = fis[col].dropna()
                prev = s[s.index.year == year - 1]
                nxt = s[s.index.year == year + 1]
                r[f"{key}_{year - 1}"] = float(prev.iloc[0]) if len(prev) else np.nan
                r[f"{key}_{year + 1}_proj"] = float(nxt.iloc[0]) if len(nxt) else np.nan
        d_de = de.loc[:d].dropna(how="all").iloc[-1]
        d_us = us.loc[:d].dropna(how="all").iloc[-1]
        r["spread_10y_vs_DE_bp"] = (r["y10"] - float(d_de[10.0])) * 100
        r["spread_10y_vs_US_bp"] = (r["y10"] - float(d_us[10.0])) * 100
        ch = p[10.0].diff().dropna()
        ch = ch[ch.index > d - pd.DateOffset(years=1)]
        ppy = len(ch)
        r["vol_10y_bp_ann"] = float(ch.std() * 100 * np.sqrt(ppy)) if ppy > 10 else np.nan
        s2 = (p[10.0] - p[2.0]).diff().dropna()
        s2 = s2[s2.index > d - pd.DateOffset(years=1)]
        r["vol_2s10s_bp_ann"] = float(s2.std() * 100 * np.sqrt(len(s2))) if len(s2) > 10 else np.nan
        # FX-hedged 10y yield for EUR and USD based investors (CIP with short-rate proxies)
        fr_local = float(M.funding_rate(m).loc[:d].iloc[-1])
        fr_eur = float(M.funding_rate("DE").loc[:d].iloc[-1])
        fr_usd = float(M.funding_rate("US").loc[:d].iloc[-1])
        r["funding_rate"] = fr_local
        r["hedged_10y_in_EUR"] = r["y10"] - (fr_local - fr_eur)
        r["hedged_10y_in_USD"] = r["y10"] - (fr_local - fr_usd)
        rows.append(r)
    return pd.DataFrame(rows)


def spread_history(pairs=(("FR", "DE"), ("PL", "DE"), ("PL", "FR"), ("UK", "DE"), ("US", "DE")),
                   tenor: float = 10.0, freq: str = "W-FRI") -> pd.DataFrame:
    out = {}
    for a, b in pairs:
        pa = M.cm_panel(a)[tenor].resample(freq).last()
        pb = M.cm_panel(b)[tenor].resample(freq).last()
        out[f"{a}-{b}"] = (pa - pb) * 100
    return pd.DataFrame(out)


def fx_vol(ccy: str = "PLN", window: int = 252) -> pd.Series:
    fx = Panel.load("fx_eur").data[ccy].dropna()
    r = np.log(fx).diff()
    return (r.rolling(window).std() * np.sqrt(252) * 100).dropna()
