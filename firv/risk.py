"""Risk analytics for single instruments and multi-leg trades, by full revaluation.

A :class:`Trade` is a list of :class:`Leg` (instrument, notional). Curves come as a dict
``{key: Curve}`` so one trade can span several curves (two countries, a bond and a swap
curve, a nominal and a real curve).

Sign convention: DV01 = value gain when the relevant rates FALL by 1 bp (a long bond has a
positive DV01). Two DV01 measures are kept apart on purpose:

* yield DV01 (:func:`leg_yield_dv01`) - per bp of each instrument's own yield to maturity
  (street convention) or par swap rate. Trades are SIZED with it, because "10k DV01 per
  bp of 2s10s" is quoted in bp of yields;
* zero-curve DV01 (:func:`dv01`, :func:`key_rate_dv01`) - per bp parallel or key-rate
  shift of the continuously compounded zero curve (triangular bumps, Ho 1992). Risk
  aggregation, scenario P&L and volatility use it; key rates sum to the parallel DV01.

For a bond the two differ by roughly the factor (1 + y/f).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

KEY_TENORS = (0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0)
BP = 1e-4


@dataclass
class Leg:
    instrument: object
    notional: float               # face amount; negative = short / pay fixed
    label: str = ""

    def value(self, curves: dict, spread: float = 0.0) -> float:
        return self.notional * self.instrument.pv(curves, spread)


@dataclass
class Trade:
    legs: list[Leg] = field(default_factory=list)
    name: str = ""
    currency: str = ""
    notes: str = ""

    def value(self, curves: dict) -> float:
        return float(sum(l.value(curves) for l in self.legs))

    @property
    def curve_keys(self):
        keys = []
        for l in self.legs:
            k = l.instrument.curve
            if k not in keys:
                keys.append(k)
        return keys

    def aged(self, h: float) -> "Trade":
        return Trade([Leg(l.instrument.aged(h), l.notional, l.label) for l in self.legs],
                     self.name, self.currency, self.notes)

    def describe(self, curves: dict) -> list[dict]:
        rows = []
        for l in self.legs:
            ins = l.instrument
            rows.append({"leg": l.label or getattr(ins, "label", ""), "kind": ins.kind,
                         "curve": ins.curve, "tenor": getattr(ins, "T", getattr(getattr(ins, "ctd", None), "T", None)),
                         "notional": l.notional,
                         "dv01": leg_dv01(l, curves)})
        return rows


def _bump(curves: dict, keys, fn) -> dict:
    out = dict(curves)
    for k in keys:
        out[k] = curves[k].shifted(fn)
    return out


def _parallel(curves: dict, keys, shift: float) -> dict:
    return _bump(curves, keys, lambda t, s=shift: np.full_like(np.asarray(t, float), s))


def leg_dv01(leg: Leg, curves: dict) -> float:
    """Zero-curve DV01 of one leg (parallel shift of the leg's own curve)."""
    k = [leg.instrument.curve]
    up = leg.value(_parallel(curves, k, +0.5 * BP), 0.0)
    dn = leg.value(_parallel(curves, k, -0.5 * BP), 0.0)
    return dn - up


def leg_yield_dv01(leg: Leg, curves: dict) -> float:
    """Yield DV01 of one leg: notional x the instrument's own-yield DV01."""
    return leg.notional * leg.instrument.yield_dv01(curves)


def yield_dv01_by_leg(trade: Trade, curves: dict) -> list[float]:
    return [leg_yield_dv01(l, curves) for l in trade.legs]


def dv01(trade: Trade, curves: dict, keys=None) -> float:
    """Value gain for a 1 bp parallel fall of all (or the given) curves."""
    keys = list(keys) if keys is not None else trade.curve_keys
    return trade.value(_parallel(curves, keys, -0.5 * BP)) - trade.value(_parallel(curves, keys, 0.5 * BP))


def dv01_by_curve(trade: Trade, curves: dict) -> dict:
    return {k: dv01(trade, curves, [k]) for k in trade.curve_keys}


def key_rate_dv01(trade: Trade, curves: dict, key_tenors=KEY_TENORS, curve_key=None) -> dict:
    """{curve: array of DV01s at each key tenor}."""
    keys = [curve_key] if curve_key else trade.curve_keys
    kt = np.asarray(key_tenors, float)
    out = {}
    for k in keys:
        vals = []
        for i in range(len(kt)):
            e = np.zeros(len(kt))
            e[i] = 1.0
            up = dict(curves)
            dn = dict(curves)
            up[k] = curves[k].key_rate_bumped(kt, e * 0.5 * BP)
            dn[k] = curves[k].key_rate_bumped(kt, -e * 0.5 * BP)
            vals.append(trade.value(dn) - trade.value(up))
        out[k] = np.array(vals)
    return out


def duration_convexity(trade: Trade, curves: dict, keys=None, h: float = 10 * BP) -> dict:
    """Modified duration and convexity with respect to a parallel zero-rate shift, from
    central differences of the full value (meaningful for positions with non-zero value)."""
    keys = list(keys) if keys is not None else trade.curve_keys
    v0 = trade.value(curves)
    vu = trade.value(_parallel(curves, keys, h))
    vd = trade.value(_parallel(curves, keys, -h))
    d1 = (vd - vu) / (2 * h)
    d2 = (vu + vd - 2 * v0) / (h * h)
    out = {"value": v0, "dvdy": -d1, "gamma_1bp": d2 * BP * BP}
    if abs(v0) > 1e-12:
        out["duration"] = d1 / v0
        out["convexity"] = d2 / v0
    return out


def spread_dv01(trade: Trade, curves: dict) -> float:
    """Value gain for a 1 bp fall in z-spreads of credit legs (government curve fixed)."""
    up = sum(l.notional * l.instrument.pv(curves, 0.5 * BP) for l in trade.legs if l.instrument.kind == "credit")
    dn = sum(l.notional * l.instrument.pv(curves, -0.5 * BP) for l in trade.legs if l.instrument.kind == "credit")
    return float(dn - up)


def inflation_dv01(trade: Trade, curves: dict, real_key: str = "real") -> float:
    """Value gain for a 1 bp RISE in breakevens with nominal yields fixed, i.e. real zero
    rates 1 bp lower. Only linker legs respond."""
    if real_key not in curves:
        return 0.0
    return dv01(trade, curves, [real_key])


# ------------------------------------------------------------------------------ carry & roll
def carry_roll(trade: Trade, curves: dict, horizon: float, funding: dict | None = None) -> dict:
    """Expected P&L over ``horizon`` years if curves do not change (same yields at the same
    time-to-maturity), split into carry and roll-down.

    funding: {curve_key: annual money-market rate} used to finance (or invest) each leg's
    dirty value; defaults to the curve's own simple rate to the horizon. Swaps and futures
    need no financing (zero upfront value at inception).

    carry     = value change if every bond kept its own yield to maturity + coupons - financing
    roll-down = extra value from rolling down an unchanged curve (total - carry)
    """
    funding = funding or {}
    total = carry = 0.0
    rows = []
    for leg in trade.legs:
        ins = leg.instrument
        k = ins.curve
        v0 = ins.pv(curves)
        aged = ins.aged(horizon)
        v_roll = aged.pv(curves)
        cash = ins.cash_in(horizon)
        if ins.kind in ("bond", "linker", "credit"):
            r = funding.get(k, float(curves[k].forward_simple(0.0, horizon)))
            fin = v0 * r * horizon
            # constant-yield value: shift the curve so that the aged bond keeps today's ytm
            v_const = _constant_yield_value(ins, curves, horizon)
            leg_total = v_roll + cash - v0 - fin
            leg_carry = v_const + cash - v0 - fin
        elif ins.kind == "swap":
            # receiver: carry = fixed accrual minus the floating rate fixed today;
            # roll = revaluation of the shorter swap on the unchanged curve
            r = funding.get(k, float(curves[k].forward_simple(0.0, horizon)))
            leg_carry = (ins.fixed_rate - r) * horizon
            leg_total = leg_carry + (v_roll - v0)
        elif ins.kind == "future":
            leg_total = v_roll - v0
            leg_carry = 0.0
        else:
            leg_total = leg_carry = 0.0
        rows.append({"leg": leg.label, "total": leg.notional * leg_total,
                     "carry": leg.notional * leg_carry,
                     "roll": leg.notional * (leg_total - leg_carry)})
        total += leg.notional * leg_total
        carry += leg.notional * leg_carry
    return {"horizon": horizon, "total": total, "carry": carry, "roll": total - carry, "legs": rows}


def _constant_yield_value(ins, curves: dict, h: float) -> float:
    """Value after h years if the instrument's own yield stays where it is today."""
    from scipy.optimize import brentq
    times, amounts = _flows(ins)
    if not len(times):
        return 0.0
    v0 = ins.pv(curves)
    f = getattr(ins, "freq", 2)
    expo = times * f

    def price(y, ex):
        return float(np.sum(amounts / (1 + y / f) ** ex))

    y = brentq(lambda yy: price(yy, expo) - v0, -0.5, 2.0, xtol=1e-12)
    keep = times > h + 1e-9
    return price(y, (times[keep] - h) * f) if keep.any() else 0.0


def _flows(ins):
    from .instruments import _bond_flows
    if ins.kind == "bond" or ins.kind == "credit":
        t, a, _ = _bond_flows(ins.T, ins.coupon, ins.freq)
    elif ins.kind == "linker":
        t, a, _ = _bond_flows(ins.T, ins.real_coupon, ins.freq)
    else:
        return np.array([]), np.array([])
    return t, a


# ------------------------------------------------------------------------------ scenarios
def scenario_pnl(trade: Trade, curves: dict, shocked: dict, horizon: float = 0.0,
                 funding: dict | None = None) -> dict:
    """P&L of moving from ``curves`` to ``shocked`` (dict of curves, same keys or a subset).

    With horizon > 0 the shock happens at the horizon: P&L = carry and roll to the horizon
    plus the revaluation of the aged trade on the shocked curves."""
    new = dict(curves)
    new.update(shocked)
    if horizon <= 0:
        pnl = trade.value(new) - trade.value(curves)
        return {"pnl": pnl, "shock": pnl, "carry_roll": 0.0}
    cr = carry_roll(trade, curves, horizon, funding)
    aged = trade.aged(horizon)
    shock = aged.value(new) - aged.value(curves)
    return {"pnl": cr["total"] + shock, "shock": shock, "carry_roll": cr["total"]}


def approx_pnl(trade: Trade, curves: dict, shocks_bp: dict, key_tenors=KEY_TENORS) -> float:
    """First-order P&L from key-rate DV01s: -sum KRD_i * shock_i (shock in bp, + = up)."""
    krd = key_rate_dv01(trade, curves, key_tenors)
    total = 0.0
    for k, v in krd.items():
        s = np.asarray(shocks_bp.get(k, np.zeros(len(key_tenors))), float)
        total += -float(np.dot(v, s))
    return total


# ------------------------------------------------------------------------------ comparison
def pnl_vol(krd: dict, cov: dict, key_tenors=KEY_TENORS) -> float:
    """Daily P&L standard deviation from key-rate DV01s and a covariance of daily zero-rate
    changes (bp^2) at the key tenors. ``cov`` maps a tuple of curve keys to a (stacked)
    covariance matrix whose order is curve-major."""
    keys = tuple(krd.keys())
    if keys not in cov:
        raise KeyError(f"covariance for curves {keys} not supplied")
    v = np.concatenate([krd[k] for k in keys])
    c = np.asarray(cov[keys], float)
    return float(np.sqrt(max(v @ c @ v, 0.0)))


def risk_report(trade: Trade, curves: dict, horizon: float = 0.25, funding: dict | None = None,
                key_tenors=KEY_TENORS, cov: dict | None = None) -> dict:
    """Everything the trade builder shows: DV01 by curve, key-rate profile, carry and roll
    over the horizon (also in bp of the largest leg DV01), and, if a covariance is given,
    daily P&L volatility and carry per unit of volatility."""
    by_curve = dv01_by_curve(trade, curves)
    krd = key_rate_dv01(trade, curves, key_tenors)
    cr = carry_roll(trade, curves, horizon, funding)
    leg_y = yield_dv01_by_leg(trade, curves)
    scale = max(abs(x) for x in leg_y) if leg_y else 0.0
    rep = {
        "value": trade.value(curves),
        "dv01": sum(by_curve.values()),
        "dv01_by_curve": by_curve,
        "yield_dv01_by_leg": leg_y,
        "key_rate_dv01": {k: v.tolist() for k, v in krd.items()},
        "key_tenors": list(key_tenors),
        "carry_roll": cr,
        "carry_roll_bp": (cr["total"] / scale) if scale else 0.0,
        "leg_dv01_max": scale,
    }
    if cov is not None:
        vol = pnl_vol(krd, cov, key_tenors)
        rep["daily_vol"] = vol
        rep["annual_vol"] = vol * np.sqrt(252)
        rep["carry_to_vol"] = (cr["total"] / horizon) / (vol * np.sqrt(252)) if vol > 0 else np.nan
        rep["breakeven_bp"] = cr["total"] / scale if scale else np.nan
    return rep
