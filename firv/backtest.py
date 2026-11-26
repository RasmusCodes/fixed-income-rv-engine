"""Backtests of DV01-weighted spread trades on constant-maturity yields.

A trade is a set of legs (series, tenor, DV01 weight); weight +1 means long one unit of
DV01 at that point (long bonds / receive fixed / long linker). P&L is measured in basis
points per unit of DV01, so 1.0 = one DV01 of money (e.g. 10,000 for a 10k-DV01 trade).

Daily P&L of leg i, held with position q_i from the previous close:

    q_i * ( -dy_i  +  0.5 * (C_i/D_i) * dy_i^2 * 1e-4  +  (carry_i + roll_i) * days )

dy in bp; D, C the modified duration and convexity of a par bond at the leg's yield;
carry_i = (y_i - funding) / (365 D_i) and roll_i = slope of the curve at the leg's tenor /
365, both in bp per day. Positions are decided at each rebalance date using data up to
that close and earn P&L from the next observation (no look-ahead).

Costs: every change of position pays the one-way bid/offer cost per leg (bp of yield, see
:data:`COSTS_BP`), and holding a constant-maturity position pays a round trip every
``roll_months`` months to roll into the new benchmark. Costs are estimates except for
Poland, where they come from the BondSpot fixing's own bid and offer yields.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Callable

import numpy as np
import pandas as pd

from .stats import summarize

# One-way transaction cost (half bid/offer, bp of yield) by market and tenor - assumptions
COSTS_BP = {
    "US": {2: 0.20, 5: 0.25, 10: 0.25, 30: 0.40},
    "DE": {2: 0.30, 5: 0.30, 10: 0.35, 30: 0.50},
    "FR": {2: 0.40, 5: 0.40, 10: 0.45, 30: 0.70},
    "UK": {2: 0.30, 5: 0.30, 10: 0.40, 30: 0.60},
    "JP": {2: 0.50, 5: 0.50, 10: 0.50, 30: 0.80},
    "PL": {2: 1.50, 5: 1.75, 10: 2.25, 20: 3.00},     # replaced by measured values when available
    "US_SWAP": {2: 0.20, 10: 0.25, 30: 0.40},
    "UK_OIS": {2: 0.20, 10: 0.30, 30: 0.40},
    "US_REAL": {5: 1.00, 10: 1.00, 30: 1.50},
    "UK_REAL": {5: 1.00, 10: 1.00, 30: 1.50},
}


def _load_measured_costs():
    """Replace the Polish placeholder costs with the ones measured from the fixing."""
    import json
    from .data.http import PROCESSED
    p = PROCESSED / "pl_costs.json"
    if p.exists():
        tab = json.loads(p.read_text()).get("one_way_bp_by_tenor", {})
        if tab:
            COSTS_BP["PL"] = {int(k): float(v) for k, v in tab.items()}


_load_measured_costs()


def cost_bp(series: str, tenor: float) -> float:
    table = COSTS_BP.get(series) or COSTS_BP.get(series.split("_")[0]) or {10: 0.5}
    keys = np.array(sorted(table))
    return float(np.interp(tenor, keys, [table[k] for k in keys]))


@dataclass(frozen=True)
class Leg:
    series: str
    tenor: float
    weight: float
    freq: int = 2


@dataclass
class Spec:
    name: str
    legs: list
    signal: str = "meanrev"           # meanrev | carry | momentum | static
    lookback: int = 52                # in rebalance periods (weeks)
    entry: float = 1.5
    exit: float = 0.25
    rebalance: str = "W-FRI"
    roll_months: int = 3
    cost_scale: float = 1.0
    weights_fn: Callable | None = None   # (date, yields history) -> weights, else leg weights
    notes: str = ""


@dataclass
class Inputs:
    """Aligned data for a backtest: yields (%) per leg column, funding (%) per leg column,
    curve slope at each leg's tenor (% per year of maturity)."""
    yields: pd.DataFrame
    funding: pd.DataFrame
    slope: pd.DataFrame
    meta: dict = field(default_factory=dict)


# ----------------------------------------------------------------------------- par bond risk
def par_duration(y_pct, T, freq):
    """Modified duration of a par bond (coupon = yield) - vectorised."""
    y = np.maximum(np.asarray(y_pct, float) / 100.0, 1e-6)
    n = np.asarray(T, float) * freq
    v = (1.0 + y / freq) ** (-n)
    small = np.abs(np.asarray(y_pct, float)) < 1e-4
    return np.where(small, np.asarray(T, float), (1.0 - v) / y)


def par_convexity(y_pct, T, freq, h=1e-4):
    """Convexity of a par bond by central differences of its price in its own yield."""
    y = np.asarray(y_pct, float) / 100.0
    c = y.copy()

    def price(yy):
        n = int(round(float(np.max(T)) * freq))
        k = np.arange(1, n + 1)[None, :]
        nn = np.asarray(T, float)[..., None] * freq
        mask = k <= nn + 1e-9
        disc = (1.0 + yy[..., None] / freq) ** (-k)
        cpn = (c[..., None] / freq) * disc * mask
        last = (1.0 + yy / freq) ** (-np.asarray(T, float) * freq)
        return cpn.sum(-1) + last

    p0, pu, pd_ = price(y), price(y + h), price(y - h)
    return (pu + pd_ - 2 * p0) / (h * h * p0)


# ----------------------------------------------------------------------------- engine
_PREP_CACHE: dict = {}


def _prep(spec: Spec, inp: Inputs) -> dict:
    """Per-leg P&L per unit of DV01, carry/roll and calendars (cached per data + legs)."""
    key = (id(inp), tuple(spec.legs), spec.rebalance, spec.roll_months)
    hit = _PREP_CACHE.get(key)
    if hit is not None and hit["inp"] is inp:       # guard against id() reuse after GC
        return hit
    if len(_PREP_CACHE) > 64:
        _PREP_CACHE.clear()
    Y = inp.yields
    legs = spec.legs
    T = np.array([l.tenor for l in legs])
    F = np.array([l.freq for l in legs])
    Yv = Y.to_numpy(float)
    dy = np.vstack([np.zeros(Yv.shape[1]), np.diff(Yv, axis=0)]) * 100.0          # bp
    days = np.r_[0, np.diff(Y.index.values).astype("timedelta64[D]").astype(float)]
    D = par_duration(Yv, T[None, :], F[None, :])
    C = np.column_stack([par_convexity(Yv[:, j], np.full(len(Y), T[j]), F[j]) for j in range(len(legs))])
    carry = (Yv - inp.funding.to_numpy(float)) * 100.0 / (365.0 * D)            # bp/day
    roll = inp.slope.to_numpy(float) * 100.0 / 365.0                          # bp/day
    accr = np.vstack([np.zeros(Yv.shape[1]), (carry + roll)[:-1] * days[1:, None]])
    per_unit = np.nan_to_num(-dy + 0.5 * (C / D) * dy ** 2 * 1e-4 + accr)
    s = pd.Series(np.arange(len(Y)), index=Y.index)
    reb_idx = s.groupby(pd.Grouper(freq=spec.rebalance)).last().dropna().astype(int).to_numpy()
    month_end = s.groupby(pd.Grouper(freq="ME")).last().dropna().astype(int).to_numpy()
    roll_days = month_end[spec.roll_months - 1::spec.roll_months] if spec.roll_months else np.array([], int)
    out = {"Yv": Yv, "per_unit": per_unit, "carry": carry, "roll": roll, "reb_idx": reb_idx,
           "roll_days": roll_days, "index": Y.index, "pnl_parts": {"dy": dy, "accr": accr},
           "inp": inp}
    _PREP_CACHE[key] = out
    return out


def run(spec: Spec, inp: Inputs, start=None, end=None) -> pd.DataFrame:
    pr = _prep(spec, inp)
    Yv, per_unit, reb_idx = pr["Yv"], pr["per_unit"], pr["reb_idx"]
    n, k = Yv.shape
    base_w = np.array([l.weight for l in spec.legs], float)
    costs = np.array([cost_bp(l.series, l.tenor) for l in spec.legs]) * spec.cost_scale
    end_i = n - 1 if end is None else int(np.searchsorted(pr["index"], pd.Timestamp(end), side="right")) - 1

    q = np.zeros(k)
    p = 0.0
    nreb = len(reb_idx)
    Qr = np.zeros((nreb, k))
    Pr = np.zeros(nreb)
    Zr = np.full(nreb, np.nan)
    Xr = np.full(nreb, np.nan)
    Cr = np.zeros(nreb)
    const = spec.weights_fn is None
    if const:
        xs_all = -(Yv[reb_idx] @ base_w) * 100.0
    for r, i in enumerate(reb_idx):
        if i > end_i:
            Qr[r:], Pr[r:] = q, p
            break
        lo = max(0, r - spec.lookback)
        if const:
            w = base_w
            xs = xs_all[lo:r + 1]
        else:
            w = np.asarray(spec.weights_fn(pr["index"][i], inp.yields.iloc[: i + 1]), float)
            xs = -(Yv[reb_idx[lo:r + 1]] @ w) * 100.0
        x_now = xs[-1]
        Xr[r] = x_now
        new_p = p
        if spec.signal == "static":
            new_p = 1.0
        elif spec.signal == "meanrev":
            if len(xs) - 1 >= max(10, spec.lookback // 2) and np.all(np.isfinite(xs)):
                mu, sd = xs[:-1].mean(), xs[:-1].std(ddof=1)
                z = (x_now - mu) / sd if sd > 0 else 0.0
                Zr[r] = z
                if p == 0.0:
                    if abs(z) > spec.entry:
                        new_p = -float(np.sign(z))
                elif np.sign(z) != -np.sign(p) or abs(z) < spec.exit:
                    new_p = -float(np.sign(z)) if abs(z) > spec.entry else 0.0
        elif spec.signal == "carry":
            exp_cr = float(np.nansum(w * (pr["carry"][i] + pr["roll"][i]))) * 30.0
            new_p = float(np.sign(exp_cr))
            Zr[r] = exp_cr
        elif spec.signal == "momentum":
            if len(xs) > 13 and np.isfinite(xs[-14]):
                new_p = float(np.sign(x_now - xs[-14]))
        new_q = new_p * w
        Cr[r] = float(np.sum(np.abs(new_q - q) * costs))
        q, p = new_q, new_p
        Qr[r], Pr[r] = q, p
    # expand to every observation: position from the last rebalance at or before each date
    pos_idx = np.searchsorted(reb_idx, np.arange(n), side="right") - 1
    has = pos_idx >= 0
    Q = np.zeros((n, k))
    P = np.zeros(n)
    Q[has] = Qr[pos_idx[has]]
    P[has] = Pr[pos_idx[has]]
    Q[end_i + 1:] = 0.0
    P[end_i + 1:] = 0.0
    cost = np.zeros(n)
    cost[reb_idx[reb_idx <= end_i]] += Cr[: int(np.sum(reb_idx <= end_i))]
    rd = pr["roll_days"][pr["roll_days"] <= end_i]
    cost[rd] += np.sum(np.abs(Q[rd]) * costs[None, :], axis=1) * 2.0
    gross = np.r_[0.0, np.sum(Q[:-1] * per_unit[1:], axis=1)]
    Z = np.full(n, np.nan)
    X = np.full(n, np.nan)
    Z[reb_idx] = Zr
    X[reb_idx] = Xr
    out = pd.DataFrame({"gross": gross, "cost": cost, "net": gross - cost, "position": P,
                        "z": Z, "spread_bp": X}, index=pr["index"])
    out = out.iloc[: end_i + 1]
    if start is not None:
        out = out[out.index >= pd.Timestamp(start)]
    return out


def periods_per_year(idx: pd.DatetimeIndex) -> float:
    years = (idx[-1] - idx[0]).days / 365.25
    return len(idx) / years if years > 0 else 252.0


def performance(res: pd.DataFrame) -> dict:
    ppy = periods_per_year(res.index)
    out = summarize(res["net"], ppy, res["position"], res["cost"])
    g = summarize(res["gross"], ppy)
    out["gross_ann_return_bp"] = g.get("ann_return_bp", np.nan)
    out["gross_sharpe"] = g.get("sharpe", np.nan)
    return out


# ----------------------------------------------------------------------------- validation
DEFAULT_GRID = [{"lookback": lb, "entry": en, "exit": ex}
                for lb in (26, 52, 104) for en in (1.0, 1.5, 2.0) for ex in (0.0, 0.5)]


def split_test(spec: Spec, inp: Inputs, split=None, grid=DEFAULT_GRID) -> dict:
    """Choose parameters on the first half (in-sample), report them on the second half
    (out-of-sample)."""
    idx = inp.yields.index
    split = pd.Timestamp(split) if split is not None else idx[len(idx) // 2]
    best, best_sr = None, -np.inf
    for g in grid:
        sp = replace(spec, **g)
        r = run(sp, inp, end=split)
        perf = performance(r)
        sr = perf.get("sharpe", np.nan)
        if np.isfinite(sr) and sr > best_sr:
            best, best_sr = g, sr
    chosen = replace(spec, **(best or {}))
    res = run(chosen, inp)
    is_perf = performance(res[res.index <= split])
    oos_perf = performance(res[res.index > split])
    return {"params": best, "split": split, "in_sample": is_perf, "out_of_sample": oos_perf, "result": res}


def walk_forward(spec: Spec, inp: Inputs, first_test_year: int | None = None, min_years: int = 4,
                 grid=DEFAULT_GRID) -> dict:
    """Re-select parameters every year on all data before it; concatenate the following
    years' out-of-sample P&L."""
    idx = inp.yields.index
    y0 = idx[0].year + min_years if first_test_year is None else first_test_year
    pieces, chosen = [], []
    for year in range(y0, idx[-1].year + 1):
        cutoff = pd.Timestamp(f"{year - 1}-12-31")
        best, best_sr = None, -np.inf
        for g in grid:
            r = run(replace(spec, **g), inp, end=cutoff)
            sr = performance(r).get("sharpe", np.nan)
            if np.isfinite(sr) and sr > best_sr:
                best, best_sr = g, sr
        res = run(replace(spec, **(best or {})), inp)
        pieces.append(res[(res.index > cutoff) & (res.index <= pd.Timestamp(f"{year}-12-31"))])
        chosen.append({"year": year, **(best or {}), "is_sharpe": best_sr})
    oos = pd.concat(pieces) if pieces else pd.DataFrame()
    return {"oos": oos, "performance": performance(oos) if len(oos) > 10 else {}, "choices": chosen}
