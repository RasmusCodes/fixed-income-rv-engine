"""Backtests of the relative-value strategy families on constant-maturity data.

Each strategy is a DV01-weighted trade (see :mod:`firv.backtest`) traded with one of three
signals: mean reversion of the trade's spread (z-score vs its own trailing history), carry
(the sign of expected carry + roll-down), and momentum (the sign of the 13-week change, a
control). A static (always-on) version shows what simply holding the trade earned.

Validation: (1) fixed default parameters over the full sample; (2) parameters chosen on
the first half, reported on the second half; (3) walk-forward re-selection each year on
all earlier data. Costs are charged at 1x the assumptions, with 0x and 2x as sensitivity.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd

from ..backtest import Spec, performance, run, split_test, walk_forward, _prep
from .common import build_inputs, leg
from ..curves.pca import pca_changes


def pca_fly_weights(tenors=(2.0, 5.0, 10.0), window: int = 504):
    """Weights (belly +1) that make a fly neutral to PC1 and PC2 estimated on the trailing
    ``window`` observations of the trade's own yields. Memoised by date (the weights
    depend only on data up to that date, not on the signal parameters)."""
    memo: dict = {}

    def fn(date, hist):
        key = (date, len(hist))
        if key not in memo:
            memo[key] = _weights(hist)
        return memo[key]

    def _weights(hist):
        h = hist.iloc[-window:]
        if len(h) < 60:
            return np.array([1.0, -0.5, -0.5])
        lv = h.copy()
        lv.columns = list(tenors)[1:2] + [tenors[0], tenors[2]]       # belly, short, long
        lv = lv[[tenors[0], tenors[1], tenors[2]]]
        r = pca_changes(lv, 2)
        L = r.loadings                                               # rows: short, belly, long
        A = np.array([[L[0, 0], L[2, 0]], [L[0, 1], L[2, 1]]])
        try:
            ws, wl = np.linalg.solve(A, np.array([L[1, 0], L[1, 1]]))
        except np.linalg.LinAlgError:
            ws, wl = 0.5, 0.5
        if not (0 < ws < 3 and 0 < wl < 3):
            ws, wl = 0.5, 0.5
        return np.array([1.0, -ws, -wl])
    return fn


def strategy_universe(markets=("US", "DE", "FR", "UK", "JP", "PL")):
    """(family, name, legs, kwargs) for every strategy studied."""
    U = []
    for m in markets:
        long_end = 10.0 if m == "PL" else 30.0      # Polish fixing has no long bonds since ~2010s
        if m == "PL":
            U.append(("curve", "PL 2s5s steepener", [leg(m, 2, 1), leg(m, 5, -1)], {}))
        U.append(("curve", f"{m} 2s10s steepener", [leg(m, 2, 1), leg(m, 10, -1)], {}))
        U.append(("curve", f"{m} 5s{long_end:g}s steepener", [leg(m, 5, 1), leg(m, long_end, -1)], {}))
        U.append(("butterfly", f"{m} 2s5s10s fly 50/50 (long belly)",
                  [leg(m, 5, 1), leg(m, 2, -0.5), leg(m, 10, -0.5)], {}))
        U.append(("butterfly", f"{m} 2s5s10s fly PCA-weighted (long belly)",
                  [leg(m, 5, 1), leg(m, 2, -0.5), leg(m, 10, -0.5)], {"weights_fn": pca_fly_weights()}))
    pairs = [("FR", "DE"), ("PL", "DE"), ("PL", "FR"), ("UK", "DE"), ("US", "DE"), ("JP", "US")]
    for a, b in pairs:
        if a in markets and b in markets:
            U.append(("cross-country", f"long {a} 10y vs short {b} 10y", [leg(a, 10, 1), leg(b, 10, -1)], {}))
    U.append(("swap spread", "US 10y swap spread (long = buy UST, pay fixed)",
              [leg("US", 10, 1), leg("US_SWAP", 10, -1)], {}))
    U.append(("swap spread", "UK 10y OIS spread (long = buy gilt, pay fixed OIS)",
              [leg("UK", 10, 1), leg("UK_OIS", 10, -1)], {}))
    U.append(("breakeven", "US 10y breakeven (long TIPS, short nominal)",
              [leg("US_REAL", 10, 1), leg("US", 10, -1)], {}))
    U.append(("breakeven", "UK 10y breakeven (long linker, short gilt)",
              [leg("UK_REAL", 10, 1), leg("UK", 10, -1)], {}))
    U.append(("credit", "US Baa vs 20y Treasury (long credit, rates-hedged)",
              [leg("US_BAA", 20, 1), leg("US", 20, -1)], {}))
    return U


def _row(family, name, signal, mode, perf, extra=None):
    r = {"family": family, "strategy": name, "signal": signal, "test": mode}
    r.update({k: v for k, v in perf.items() if not isinstance(v, (dict, list))})
    if extra:
        r.update(extra)
    return r


def run_all(markets=("US", "DE", "FR", "UK", "JP", "PL"), wf_signals=("meanrev",), log=print,
            keep_series=None):
    rows, series_out = [], {}
    for family, name, legs, kw in strategy_universe(markets):
        try:
            inp = build_inputs(legs)
        except Exception as exc:
            log(f"  skip {name}: {exc}")
            continue
        if len(inp.yields) < 300:
            log(f"  skip {name}: only {len(inp.yields)} observations")
            continue
        base = Spec(name, legs, **kw)
        weekly = (inp.yields.index.to_series().diff().dt.days.median() or 1) >= 5
        if weekly:
            base = replace(base, lookback=52)
        for signal in ("static", "meanrev", "carry", "momentum"):
            spec = replace(base, signal=signal)
            for scale in (1.0, 0.0, 2.0) if signal != "static" else (1.0,):
                res = run(replace(spec, cost_scale=scale), inp)
                rows.append(_row(family, name, signal, f"full sample, costs x{scale:g}", performance(res)))
                if scale == 1.0 and keep_series is not None and (name, signal) in keep_series:
                    series_out[(name, signal)] = res
            if signal in wf_signals:
                st = split_test(spec, inp)
                rows.append(_row(family, name, signal, "in-sample (first half, chosen params)",
                                 st["in_sample"], {"params": str(st["params"]), "split": st["split"]}))
                rows.append(_row(family, name, signal, "out-of-sample (second half)",
                                 st["out_of_sample"], {"params": str(st["params"]), "split": st["split"]}))
                wf = walk_forward(spec, inp)
                if wf["performance"]:
                    rows.append(_row(family, name, signal, "walk-forward OOS", wf["performance"],
                                     {"params": "re-selected yearly"}))
        log(f"  done {name} ({len(inp.yields)} obs, {inp.yields.index[0]:%Y}-{inp.yields.index[-1]:%Y})")
    return pd.DataFrame(rows), series_out


def cross_country_carry(markets=("US", "DE", "FR", "UK", "JP"), tenor: float = 10.0,
                        vol_window: int = 252, cost_scale: float = 1.0) -> pd.DataFrame:
    """Each month: long the market whose 10y point has the highest carry+roll per unit of
    trailing yield volatility, short the lowest (DV01-neutral, local-currency bp, FX on the
    P&L ignored). P&L per unit of DV01 per leg."""
    from ..backtest import cost_bp
    legs = [leg(m, tenor, 1.0) for m in markets]
    inp = build_inputs(legs, start="2000-01-01")
    spec = Spec("xc carry", legs, signal="static")
    pr = _prep(spec, inp)
    per_unit, carry, roll = pr["per_unit"], pr["carry"], pr["roll"]
    idx = inp.yields.index
    vol = pd.DataFrame(inp.yields.diff().to_numpy() * 100, index=idx).rolling(vol_window).std().to_numpy()
    month_end = pd.Series(np.arange(len(idx)), index=idx).groupby(pd.Grouper(freq="ME")).last().dropna().astype(int).to_numpy()
    q = np.zeros(len(markets))
    Q = np.zeros((len(idx), len(markets)))
    cost = np.zeros(len(idx))
    costs = np.array([cost_bp(m, tenor) for m in markets]) * cost_scale
    last = 0
    for i in month_end:
        Q[last:i + 1] = q
        if np.all(np.isfinite(vol[i])):
            score = (carry[i] + roll[i]) * 30.0 / vol[i]
            new = np.zeros(len(markets))
            new[int(np.argmax(score))] = 1.0
            new[int(np.argmin(score))] = -1.0
            cost[i] += float(np.sum(np.abs(new - q) * costs))
            q = new
        last = i + 1
    Q[last:] = q
    gross = np.r_[0.0, np.sum(Q[:-1] * per_unit[1:], axis=1)]
    return pd.DataFrame({"gross": gross, "cost": cost, "net": gross - cost,
                         "position": np.abs(Q).sum(axis=1) / 2}, index=idx)
