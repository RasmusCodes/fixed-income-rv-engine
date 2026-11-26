import datetime as dt

import numpy as np
import pytest

from firv.bonds import Bond
from firv.curves import Svensson, ZeroCurve
from firv.instruments import CMBond, Swap, conversion_factor, par_bond, par_swap
from firv.risk import (KEY_TENORS, Leg, Trade, carry_roll, dv01, key_rate_dv01, scenario_pnl)
from firv.strategies import (basis_trade, breakeven_trade, butterfly, credit_trade, curve_trade,
                             factor_trade, implied_repo, net_basis, spread_trade, swap_spread_trade)

CURVE = Svensson(0.042, -0.012, 0.015, -0.010, 1.6, 9.0)
FLAT = ZeroCurve([0.1, 60.0], [0.04, 0.04])
CURVES = {"g": CURVE, "s": CURVE.shifted(0.003), "real": CURVE.shifted(-0.022), "repo": CURVE}


def test_key_rates_sum_to_parallel_dv01():
    tr = Trade([Leg(par_bond(CURVES, "g", 7.0), 1e6), Leg(par_bond(CURVES, "g", 23.0), -4e5)])
    total = dv01(tr, CURVES)
    gross = sum(abs(dv01(Trade([l]), CURVES)) for l in tr.legs)
    krd = key_rate_dv01(tr, CURVES)["g"]
    assert abs(krd.sum() - total) < 1e-6 * gross


def test_curve_dv01_close_to_yield_dv01_for_par_bond():
    b = par_bond({"f": FLAT}, "f", 10.0, 1)
    tr = Trade([Leg(b, 100.0)])
    y = float(np.exp(0.04) - 1)          # annual yield equal to the flat continuous rate
    bond = Bond(dt.date(2036, 1, 1), b.coupon, 1)
    ydv01 = bond.risk(y, dt.date(2026, 1, 1))["dv01"]
    # curve DV01 is per bp of continuous zero rate; yield DV01 per bp of annual yield
    assert dv01(tr, {"f": FLAT}) == pytest.approx(ydv01 * (1 + y), rel=2e-3)


def test_steepener_is_dv01_neutral_and_pays_on_steepening():
    from firv.risk import yield_dv01_by_leg
    tr = curve_trade(CURVES, "g", 2.0, 10.0, dv01=10_000, direction="steepener")
    legs = yield_dv01_by_leg(tr, CURVES)
    assert legs[0] == pytest.approx(10_000) and legs[1] == pytest.approx(-10_000)
    # zero-curve DV01 is not exactly zero (the (1+y/f) factors differ by tenor) but small
    assert abs(dv01(tr, CURVES)) < 0.005 * 10_000
    steeper = {"g": CURVES["g"].key_rate_bumped([2.0, 10.0], [0.0, 0.0010])}
    pnl = scenario_pnl(tr, CURVES, steeper)["pnl"]
    # P&L = dv01 x change in the 2s10s par spread (bp)
    d_spread = ((steeper["g"].par_yield(10.0, 2) - CURVES["g"].par_yield(10.0, 2))
                - (steeper["g"].par_yield(2.0, 2) - CURVES["g"].par_yield(2.0, 2))) * 1e4
    assert pnl == pytest.approx(10_000 * d_spread, rel=0.01)


def test_butterfly_weightings():
    from firv.risk import yield_dv01_by_leg
    fly = butterfly(CURVES, "g", (2.0, 10.0), 5.0, dv01=10_000, weighting="50/50")
    assert np.allclose(yield_dv01_by_leg(fly, CURVES), [10_000, -5_000, -5_000])
    L = np.array([[0.30, -0.45], [0.36, -0.05], [0.33, 0.40]])           # PC1, PC2 at 2/5/10
    pfly = butterfly(CURVES, "g", (2.0, 10.0), 5.0, dv01=10_000, weighting="pca", loadings=L)
    # DV01 vector of legs, in the order belly, short wing, long wing -> tenors 5, 2, 10
    d = np.array(yield_dv01_by_leg(pfly, CURVES))
    expo = d[0] * L[1] + d[1] * L[0] + d[2] * L[2]
    assert np.allclose(expo, 0.0, atol=1e-6 * 10_000)


def test_factor_trade_loads_only_on_target():
    tenors = [2.0, 5.0, 10.0, 30.0]
    L = np.array([[0.45, -0.5, 0.4], [0.5, -0.1, -0.5], [0.5, 0.3, -0.2], [0.45, 0.6, 0.5]])
    tr = factor_trade(CURVES, "g", tenors, L, target_factor=1, dv01=5_000)
    from firv.risk import yield_dv01_by_leg
    d = np.array(yield_dv01_by_leg(tr, CURVES))
    expo = -(L.T @ d)                     # P&L per unit factor move (yields up = +)
    assert expo[1] == pytest.approx(5_000, rel=1e-6)
    assert abs(expo[0]) < 1e-3 and abs(expo[2]) < 1e-3


def test_carry_roll_flat_curve_and_upward_curve():
    b = par_bond({"f": FLAT}, "f", 10.0, 2)
    tr = Trade([Leg(b, 1.0)])
    fund = float(FLAT.forward_simple(0.0, 0.25))
    cr = carry_roll(tr, {"f": FLAT}, 0.25, {"f": fund})
    assert abs(cr["roll"]) < 2e-5 and abs(cr["total"]) < 2e-4
    up = ZeroCurve([0.25, 2, 10, 30], [0.02, 0.03, 0.04, 0.045])
    b2 = par_bond({"u": up}, "u", 10.0, 2)
    cr2 = carry_roll(Trade([Leg(b2, 1.0)]), {"u": up}, 0.25)
    assert cr2["carry"] > 0 and cr2["roll"] > 0


def test_parallel_scenario_matches_dv01_to_first_order():
    tr = Trade([Leg(par_bond(CURVES, "g", 10.0), 1e6)])
    d = dv01(tr, CURVES)
    pnl = scenario_pnl(tr, CURVES, {"g": CURVES["g"].shifted(0.0001)})["pnl"]
    assert pnl == pytest.approx(-d, rel=0.01)


def test_swap_par_value_and_swap_spread_trade():
    sw = par_swap(CURVES, "s", 10.0, 1)
    assert sw.pv(CURVES) == pytest.approx(0.0, abs=1e-12)
    tr = swap_spread_trade(CURVES, "g", "s", 10.0, dv01=10_000)
    from firv.risk import yield_dv01_by_leg
    assert np.allclose(yield_dv01_by_leg(tr, CURVES), [10_000, -10_000])
    wider = {"s": CURVES["s"].shifted(0.0005)}           # swap curve up 5bp, bonds unchanged
    d_spread = (wider["s"].par_yield(10.0, 1) - CURVES["s"].par_yield(10.0, 1)) * 1e4
    assert scenario_pnl(tr, CURVES, wider)["pnl"] == pytest.approx(10_000 * d_spread, rel=0.02)


def test_conversion_factor():
    assert conversion_factor(0.06, 9, 0) == pytest.approx(1.0)
    assert conversion_factor(0.06, 9, 9) == pytest.approx(1.0, abs=1e-4)
    # equals the clean price per 1 at a 6% semiannual yield of a bond with that maturity
    for cpn, n, z in [(0.04375, 8, 3), (0.025, 7, 0), (0.05, 9, 6), (0.0425, 6, 9)]:
        settle = dt.date(2026, 12, 1)
        mat = dt.date(2026 + n + (z + 12 - 1) // 12, (12 - 1 + z) % 12 + 1, 1)
        b = Bond(mat, cpn, 2)
        assert conversion_factor(cpn, n, z) == pytest.approx(b.clean_from_yield(0.06, settle) / 100, abs=1.5e-4)


def test_futures_basis_consistency():
    ctd = par_bond(CURVES, "g", 7.3)
    cf = conversion_factor(ctd.coupon, 7, 3)
    from firv.instruments import BondFuture
    fut = BondFuture(ctd, cf, 0.25, "repo")
    fair = fut.fair_price(CURVES)
    repo = float(CURVES["repo"].zero(0.25))
    ir = implied_repo(ctd, cf, fair, 0.25, CURVES)
    # simple implied repo vs continuous repo: equal up to compounding
    assert ir == pytest.approx((np.exp(repo * 0.25) - 1) / 0.25, abs=2e-5)
    nb = net_basis(ctd, cf, fair, 0.25, CURVES, ir)
    assert abs(nb["net_basis"]) < 1e-6
    tr = basis_trade(CURVES, ctd, cf, 0.25)
    assert abs(dv01(tr, CURVES, ["g"])) < 0.05 * abs(dv01(Trade([tr.legs[0]]), CURVES))


def test_breakeven_credit_and_spread_trades():
    be = breakeven_trade(CURVES, "g", "real", 10.0, dv01=10_000)
    # breakevens +1bp with nominal fixed = real yields -1bp: gains ~10k
    pnl = scenario_pnl(be, CURVES, {"real": CURVES["real"].shifted(-0.0001)})["pnl"]
    assert pnl == pytest.approx(10_000, rel=0.02)
    cr = credit_trade(CURVES, "g", 5.0, 0.012, spread_dv01=1_000)
    assert abs(dv01(cr, CURVES)) < 50.0                     # rates-hedged
    from firv.risk import spread_dv01
    assert spread_dv01(cr, CURVES) == pytest.approx(1_000, rel=1e-6)
    sp = spread_trade(CURVES, ("g", 10.0, 1), ("s", 10.0, 1), dv01=10_000, beta=1.2)
    from firv.risk import yield_dv01_by_leg
    assert np.allclose(yield_dv01_by_leg(sp, CURVES), [10_000, -12_000])
