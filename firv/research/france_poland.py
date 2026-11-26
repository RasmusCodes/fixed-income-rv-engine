"""France versus Poland: a case study built from the comparison framework.

The two curves differ in currency (EUR vs PLN), monetary policy (ECB vs NBP), inflation,
fiscal path and liquidity, so a "spread" between them mixes several things. This module
lays out the evidence and evaluates candidate trades with the same risk and backtest
machinery as everything else; it does not start from a view.

Data: French TEC constant-maturity yields (daily, Banque de France / Euronext) sampled
weekly to match the Polish curve, which is fitted every week to the BondSpot fixing.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd

from .. import market as M
from ..backtest import Spec, performance, run, split_test, walk_forward
from ..data.loaders import Panel
from .common import build_inputs, leg
from .country import fx_vol

TENORS = (2.0, 5.0, 10.0)


def weekly_panel() -> pd.DataFrame:
    pl = M.cm_panel("PL")
    fr = M.cm_panel("FR")
    out = {}
    for T in (1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0):
        if T in pl.columns:
            out[f"PL_{T:g}"] = pl[T]
        if T in fr.columns:
            out[f"FR_{T:g}"] = fr[T].reindex(pl.index, method="ffill")
    df = pd.DataFrame(out).dropna(subset=["PL_10", "FR_10"])
    return df


def spreads(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for T in TENORS:
        out[f"PL-FR {T:g}y"] = (df[f"PL_{T:g}"] - df[f"FR_{T:g}"]) * 100
    out["PL 2s10s"] = (df["PL_10"] - df["PL_2"]) * 100
    out["FR 2s10s"] = (df["FR_10"] - df["FR_2"]) * 100
    out["slope gap (PL-FR 2s10s)"] = out["PL 2s10s"] - out["FR 2s10s"]
    return out


def co_movement(df: pd.DataFrame, window: int = 52) -> pd.DataFrame:
    dpl = df["PL_10"].diff() * 100
    dfr = df["FR_10"].diff() * 100
    cov = dpl.rolling(window).cov(dfr)
    beta = cov / dfr.rolling(window).var()
    corr = dpl.rolling(window).corr(dfr)
    return pd.DataFrame({"beta_PL_on_FR": beta, "corr": corr,
                         "vol_PL10_bp": dpl.rolling(window).std() * np.sqrt(52),
                         "vol_FR10_bp": dfr.rolling(window).std() * np.sqrt(52)})


def hedge_cost(df: pd.DataFrame) -> pd.DataFrame:
    """Short-rate differential (NBP rate minus EUR STR / Bund bill proxy) = approximate
    annual cost of hedging PLN into EUR with rolling FX forwards (covered interest parity)."""
    r_pl = M.funding_rate("PL").reindex(df.index, method="ffill")
    r_eur = M.funding_rate("DE").reindex(df.index, method="ffill")
    out = pd.DataFrame(index=df.index)
    out["r_PLN"] = r_pl
    out["r_EUR"] = r_eur
    out["hedge_cost"] = r_pl - r_eur
    out["PL10_hedged_EUR"] = df["PL_10"] - out["hedge_cost"]
    out["FR10"] = df["FR_10"]
    out["hedged_pickup_bp"] = (out["PL10_hedged_EUR"] - out["FR10"]) * 100
    return out


def candidate_trades():
    return [
        ("PL 10y vs FR 10y, DV01-neutral (long PL)", [leg("PL", 10, 1), leg("FR", 10, -1)]),
        ("PL 5y vs FR 5y, DV01-neutral (long PL)", [leg("PL", 5, 1), leg("FR", 5, -1)]),
        ("PL 2y vs FR 2y, DV01-neutral (long PL)", [leg("PL", 2, 1), leg("FR", 2, -1)]),
        ("Curve box: PL 2s10s steepener vs FR 2s10s flattener",
         [leg("PL", 2, 1), leg("PL", 10, -1), leg("FR", 2, -1), leg("FR", 10, 1)]),
        ("PL 2s10s steepener", [leg("PL", 2, 1), leg("PL", 10, -1)]),
        ("FR 2s10s steepener", [leg("FR", 2, 1), leg("FR", 10, -1)]),
    ]


def evaluate_trades(beta_window: int = 52) -> pd.DataFrame:
    rows = []
    for name, legs in candidate_trades():
        inp = build_inputs(legs)
        base = Spec(name, legs, lookback=52)
        for signal in ("static", "meanrev", "carry"):
            res = run(replace(base, signal=signal), inp)
            perf = performance(res)
            rows.append({"trade": name, "signal": signal, "test": "full sample", **{k: v for k, v in perf.items()
                                                                                    if not isinstance(v, dict)}})
            if signal == "meanrev":
                st = split_test(replace(base, signal=signal), inp)
                rows.append({"trade": name, "signal": signal, "test": "out-of-sample (second half)",
                             "params": str(st["params"]), **st["out_of_sample"]})
                wf = walk_forward(replace(base, signal=signal), inp, min_years=4)
                if wf["performance"]:
                    rows.append({"trade": name, "signal": signal, "test": "walk-forward OOS", **wf["performance"]})
    return pd.DataFrame(rows)


def macro_table() -> pd.DataFrame:
    cpi = Panel.load("cpi_yoy").data[["FR", "PL"]].dropna(how="all")
    fis = Panel.load("oecd_fiscal").data
    pol = Panel.load("policy_rates").data[["EA", "PL"]]
    rows = []
    for y in range(2015, pd.Timestamp.today().year + 2):
        r = {"year": y}
        for c in ("FR", "PL"):
            s = cpi[c][cpi.index.year == y].dropna()
            r[f"cpi_avg_{c}"] = float(s.mean()) if len(s) else np.nan
            for key, col in (("debt", f"{c}_GGFLQ"), ("maastricht_debt", f"{c}_GGFLMQ"), ("balance", f"{c}_NLGQ")):
                v = fis[col][fis.index.year == y].dropna() if col in fis.columns else pd.Series(dtype=float)
                r[f"{key}_{c}"] = float(v.iloc[0]) if len(v) else np.nan
        for c, lab in (("EA", "ECB"), ("PL", "NBP")):
            s = pol[c][pol.index.year == y].dropna()
            r[f"policy_end_{lab}"] = float(s.iloc[-1]) if len(s) else np.nan
        rows.append(r)
    return pd.DataFrame(rows)


def run_case():
    df = weekly_panel()
    sp = spreads(df)
    cm = co_movement(df)
    hc = hedge_cost(df)
    fxv = fx_vol("PLN").reindex(df.index, method="ffill")
    trades = evaluate_trades()
    macro = macro_table()
    return {"panel": df, "spreads": sp, "co_movement": cm, "hedge": hc, "fx_vol": fxv,
            "trades": trades, "macro": macro}
