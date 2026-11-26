"""Trade construction: curve trades, butterflies, PCA trades, cross-country spreads, swap
spreads, futures basis, breakevens, credit and carry/roll selection.

Every constructor sizes legs by yield DV01 (per bp of each leg's own yield, the street
convention) so that trades are comparable: ``dv01`` is the money made per 1 bp move of the
spread the trade expresses (a 2s10s steepener with dv01=10_000 makes about 10,000 per bp
of steepening in par yields). Hedge ratios are configurable:

* ``'dv01'``        - equal and opposite DV01 (neutral to parallel moves);
* ``'beta'``        - hedge leg scaled by a regression beta of yield changes;
* ``'pca'``         - neutral to chosen principal components of curve moves;
* ``'regression'``  - butterfly wings from a two-variable regression of belly on wings;
* ``'50/50'``       - butterfly wings each carry half the belly DV01.
"""
from __future__ import annotations

import itertools

import numpy as np

from .instruments import BondFuture, CMBond, CreditBond, Linker, Swap, par_bond, par_swap
from .risk import Leg, Trade, carry_roll, key_rate_dv01, leg_dv01, pnl_vol

BP = 1e-4


def unit_dv01(instrument, curves: dict) -> float:
    """Yield DV01 per unit notional (street convention)."""
    return instrument.yield_dv01(curves)


def unit_zero_dv01(instrument, curves: dict) -> float:
    """Zero-curve DV01 per unit notional (parallel shift of continuous zero rates)."""
    return leg_dv01(Leg(instrument, 1.0), curves)


def _leg_for(instrument, curves, dv01_amount, label=""):
    """Leg with the notional that gives ``dv01_amount`` (signed: + = long rates risk)."""
    u = unit_dv01(instrument, curves)
    return Leg(instrument, dv01_amount / u, label or getattr(instrument, "label", ""))


def _instrument(curves, curve, T, freq, kind="bond"):
    return par_swap(curves, curve, T, freq) if kind == "swap" else par_bond(curves, curve, T, freq)


# --------------------------------------------------------------------------- curve trades
def curve_trade(curves: dict, curve: str, short_T: float, long_T: float, dv01: float,
                direction: str = "steepener", freq: int = 2, kind: str = "bond",
                hedge: str = "dv01", beta: float = 1.0, name: str = "") -> Trade:
    """2s10s / 5s30s style trades.

    Steepener: long the short tenor, short the long tenor (gains when long - short widens).
    Flattener: the reverse. With hedge='beta' the short-tenor leg carries beta x the
    long-tenor DV01 (beta = regression of long-tenor changes on short-tenor changes inverted
    appropriately by the caller); 'dv01' uses beta = 1."""
    sign = 1.0 if direction == "steepener" else -1.0
    b = beta if hedge == "beta" else 1.0
    s_ins = _instrument(curves, curve, short_T, freq, kind)
    l_ins = _instrument(curves, curve, long_T, freq, kind)
    legs = [_leg_for(s_ins, curves, sign * dv01 * b, f"{'long' if sign > 0 else 'short'} {short_T:g}y"),
            _leg_for(l_ins, curves, -sign * dv01, f"{'short' if sign > 0 else 'long'} {long_T:g}y")]
    return Trade(legs, name or f"{curve} {short_T:g}s{long_T:g}s {direction}")


def butterfly(curves: dict, curve: str, wings: tuple, belly: float, dv01: float,
              weighting: str = "50/50", direction: str = "long_belly", freq: int = 2,
              kind: str = "bond", loadings: np.ndarray | None = None,
              regression: tuple | None = None, name: str = "") -> Trade:
    """Butterfly: belly against two wings.

    long_belly (receive/buy the belly, sell wings) gains when the belly cheapens less...
    precisely: P&L ~ dv01 * -(change in 2*belly - short wing - long wing) for 50/50.

    weighting:
      '50/50'      wings each hedge half the belly DV01;
      'dv01'       same as 50/50 (DV01-neutral) - kept for clarity;
      'regression' wing DV01s = dv01 * (b_short, b_long) from a regression of belly yield
                   changes on wing yield changes (pass ``regression=(b_short, b_long)``);
      'pca'        wings sized so the fly has zero exposure to PC1 and PC2; pass
                   ``loadings`` = 3x2 array of PC1, PC2 loadings at (short, belly, long).
    """
    s_T, l_T = wings
    sign = 1.0 if direction == "long_belly" else -1.0
    if weighting in ("50/50", "dv01"):
        ws, wl = 0.5, 0.5
    elif weighting == "regression":
        if regression is None:
            raise ValueError("regression weighting needs regression=(b_short, b_long)")
        ws, wl = regression
    elif weighting == "pca":
        if loadings is None:
            raise ValueError("pca weighting needs loadings (3 x 2) at short, belly, long")
        L = np.asarray(loadings, float)
        # belly DV01 = 1; wings w_s, w_l (as DV01 amounts, opposite sign) such that
        # w_s*L_s,f + w_l*L_l,f = L_b,f for f in (PC1, PC2)
        A = np.array([[L[0, 0], L[2, 0]], [L[0, 1], L[2, 1]]])
        rhs = np.array([L[1, 0], L[1, 1]])
        ws, wl = np.linalg.solve(A, rhs)
    else:
        raise ValueError(f"unknown weighting {weighting!r}")
    legs = [
        _leg_for(_instrument(curves, curve, belly, freq, kind), curves, sign * dv01, f"belly {belly:g}y"),
        _leg_for(_instrument(curves, curve, s_T, freq, kind), curves, -sign * dv01 * ws, f"wing {s_T:g}y"),
        _leg_for(_instrument(curves, curve, l_T, freq, kind), curves, -sign * dv01 * wl, f"wing {l_T:g}y"),
    ]
    return Trade(legs, name or f"{curve} {s_T:g}s{belly:g}s{l_T:g}s fly ({weighting})")


def factor_trade(curves: dict, curve: str, tenors, loadings: np.ndarray, target_factor: int,
                 dv01: float, freq: int = 2, kind: str = "bond", name: str = "") -> Trade:
    """Position whose DV01 profile loads only on one principal component.

    ``loadings``: n_tenors x k matrix of PC loadings (bp per unit factor) at ``tenors``.
    The DV01 vector w solves L^T w = e_target * dv01 with minimum norm, so the trade makes
    ``dv01`` per unit move of the target factor and nothing from the other k-1 factors."""
    L = np.asarray(loadings, float)
    k = L.shape[1]
    e = np.zeros(k)
    e[target_factor] = dv01
    # P&L = -sum_i w_i * dy_i with dy = L f, so exposure to factor f is -L^T w; we want +e
    w = -np.linalg.lstsq(L.T, e, rcond=None)[0]
    legs = [_leg_for(_instrument(curves, curve, T, freq, kind), curves, wi, f"{T:g}y")
            for T, wi in zip(tenors, w)]
    return Trade(legs, name or f"{curve} PC{target_factor + 1} trade")


# --------------------------------------------------------------------------- cross-market
def spread_trade(curves: dict, long_leg: tuple, short_leg: tuple, dv01: float,
                 beta: float = 1.0, fx: float = 1.0, name: str = "") -> Trade:
    """Long one bond, short another (another tenor, curve or country).

    long_leg / short_leg: (curve_key, tenor, freq). ``dv01`` is in the long leg's currency;
    the short leg's DV01 is beta * dv01 converted at ``fx`` (units of short-leg currency per
    unit of long-leg currency). beta = 1 is DV01-neutral; a regression beta hedges the
    typical co-movement instead (e.g. Poland moving more than France)."""
    (ca, ta, fa), (cb, tb, fb) = long_leg, short_leg
    a = par_bond(curves, ca, ta, fa)
    b = par_bond(curves, cb, tb, fb)
    legs = [_leg_for(a, curves, dv01, f"long {ca} {ta:g}y"),
            _leg_for(b, curves, -beta * dv01 * fx, f"short {cb} {tb:g}y")]
    return Trade(legs, name or f"{ca} {ta:g}y vs {cb} {tb:g}y")


def swap_spread_trade(curves: dict, gov: str, swap: str, T: float, dv01: float,
                      direction: str = "long_spread", gov_freq: int = 2, swap_freq: int = 1,
                      name: str = "") -> Trade:
    """Swap spread = swap rate - government par yield at the same tenor.

    long_spread: buy the bond and pay fixed on the swap (gains if the spread widens).
    short_spread: sell the bond and receive fixed."""
    sign = 1.0 if direction == "long_spread" else -1.0
    bond = par_bond(curves, gov, T, gov_freq)
    sw = par_swap(curves, swap, T, swap_freq)
    legs = [_leg_for(bond, curves, sign * dv01, f"{'buy' if sign > 0 else 'sell'} {gov} {T:g}y"),
            _leg_for(sw, curves, -sign * dv01, f"{'pay' if sign > 0 else 'receive'} {T:g}y swap")]
    return Trade(legs, name or f"{T:g}y swap spread ({direction})")


def basis_trade(curves: dict, ctd: CMBond, conversion_factor: float, delivery: float,
                face: float = 1_000_000.0, direction: str = "long_basis", repo_curve: str = "repo",
                name: str = "") -> Trade:
    """Long basis: buy the deliverable bond, sell CF x face of futures (per unit notional of
    the future the price is per 1 of face). Short basis is the reverse."""
    sign = 1.0 if direction == "long_basis" else -1.0
    fut = BondFuture(ctd, conversion_factor, delivery, repo_curve, label="future")
    legs = [Leg(ctd, sign * face, "deliverable bond"),
            Leg(fut, -sign * face * conversion_factor, "futures (CF-weighted)")]
    return Trade(legs, name or f"futures basis ({direction})")


def implied_repo(ctd: CMBond, conversion_factor: float, futures_price: float, delivery: float,
                 curves: dict) -> float:
    """Implied repo rate (simple, annualised): return from buying the bond today and
    delivering it into the futures at ``futures_price`` (coupons received count)."""
    spot_dirty = ctd.pv(curves)
    cpn = ctd.cash_in(delivery)
    invoice = futures_price * conversion_factor + ctd.aged(delivery).accrued()
    return (invoice + cpn - spot_dirty) / (spot_dirty * delivery)


def net_basis(ctd: CMBond, conversion_factor: float, futures_price: float, delivery: float,
              curves: dict, repo: float) -> dict:
    """Gross basis, carry and net basis (price per 1 face, x100 for points)."""
    spot_dirty = ctd.pv(curves)
    clean = spot_dirty - ctd.accrued()
    gross = clean - futures_price * conversion_factor
    cpn = ctd.cash_in(delivery)
    accr_end = ctd.aged(delivery).accrued()
    coupon_income = cpn + accr_end - ctd.accrued()
    financing = spot_dirty * repo * delivery
    carry = coupon_income - financing
    return {"gross_basis": gross, "carry": carry, "net_basis": gross - carry,
            "implied_repo": implied_repo(ctd, conversion_factor, futures_price, delivery, curves)}


def breakeven_trade(curves: dict, nominal: str, real: str, T: float, dv01: float,
                    beta: float = 1.0, direction: str = "long_breakeven", freq: int = 2,
                    name: str = "") -> Trade:
    """Long breakeven: buy the linker, sell nominal bonds with nominal DV01 = beta x real
    DV01 (beta = 1: pure breakeven exposure if real and nominal moved one for one)."""
    sign = 1.0 if direction == "long_breakeven" else -1.0
    rc = float(curves[real].par_yield(T, freq))
    linker = Linker(T, rc, freq, real, label=f"{T:g}y linker")
    nom = par_bond(curves, nominal, T, freq)
    legs = [_leg_for(linker, curves, sign * dv01, f"{'buy' if sign > 0 else 'sell'} {T:g}y linker"),
            _leg_for(nom, curves, -sign * beta * dv01, f"{'sell' if sign > 0 else 'buy'} {T:g}y nominal")]
    return Trade(legs, name or f"{T:g}y breakeven ({direction})")


def credit_trade(curves: dict, gov: str, T: float, z_spread: float, spread_dv01: float,
                 hedge_rates: bool = True, freq: int = 2, name: str = "") -> Trade:
    """Long a corporate bond at ``z_spread`` over ``gov``; optionally hedge its rates DV01
    with a government bond so only spread risk remains."""
    c = float(curves[gov].par_yield(T, freq)) + z_spread
    bond = CreditBond(T, c, z_spread, freq, gov, label=f"{T:g}y credit")
    # a parallel z-spread move and a parallel zero-curve move discount the same cash flows,
    # so the credit leg's spread DV01 equals its zero-curve DV01; the hedge matches it
    u = unit_zero_dv01(bond, curves)
    legs = [Leg(bond, spread_dv01 / u, f"long {T:g}y credit")]
    if hedge_rates:
        g = par_bond(curves, gov, T, freq)
        legs.append(Leg(g, -spread_dv01 / unit_zero_dv01(g, curves), f"short {T:g}y {gov}"))
    return Trade(legs, name or f"{T:g}y credit spread")


# --------------------------------------------------------------------------- carry & roll
def carry_roll_table(curves: dict, curve: str, tenors, horizon: float = 0.25, freq: int = 2,
                     cov: np.ndarray | None = None, key_tenors=None, funding: float | None = None):
    """Carry and roll-down of DV01-normalised long positions in each tenor (bp over the
    horizon), plus bp per unit of annualised yield volatility when a covariance is given."""
    rows = []
    fund = {curve: funding} if funding is not None else None
    for T in tenors:
        tr = Trade([_leg_for(par_bond(curves, curve, T, freq), curves, 1.0)], f"{T:g}y")
        cr = carry_roll(tr, curves, horizon, fund)
        row = {"tenor": T, "carry_bp": cr["carry"], "roll_bp": cr["roll"], "total_bp": cr["total"]}
        if cov is not None and key_tenors is not None:
            krd = key_rate_dv01(tr, curves, key_tenors)
            vol = pnl_vol(krd, {(curve,): cov}, key_tenors)
            row["vol_bp_annual"] = vol * np.sqrt(252)
            row["total_per_vol"] = (cr["total"] / horizon) / (vol * np.sqrt(252)) if vol > 0 else np.nan
        rows.append(row)
    return rows


def best_carry_pairs(curves: dict, curve: str, tenors, horizon: float, cov: np.ndarray,
                     key_tenors, freq: int = 2, top: int = 5):
    """All DV01-neutral two-tenor trades ranked by carry+roll per unit of P&L volatility.
    Returns (short tenor, long tenor, direction, carry+roll bp, annual vol bp, ratio)."""
    out = []
    for a, b in itertools.combinations(sorted(tenors), 2):
        for direction in ("steepener", "flattener"):
            tr = curve_trade(curves, curve, a, b, 1.0, direction, freq)
            cr = carry_roll(tr, curves, horizon)
            krd = key_rate_dv01(tr, curves, key_tenors)
            vol = pnl_vol(krd, {(curve,): cov}, key_tenors) * np.sqrt(252)
            ratio = (cr["total"] / horizon) / vol if vol > 0 else np.nan
            out.append((a, b, direction, cr["total"], vol, ratio))
    out.sort(key=lambda r: -np.nan_to_num(r[5], nan=-1e9))
    return out[:top]
