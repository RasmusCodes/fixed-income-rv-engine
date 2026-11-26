import numpy as np
import pandas as pd
import pytest

from firv.curves import (CurveData, NelsonSiegel, Svensson, ZeroCurve, bootstrap_par, fit,
                         leave_one_out)
from firv.curves.pca import decompose_move, pca_changes

TRUE = Svensson(0.042, -0.012, 0.015, -0.010, 1.6, 9.0)
TENORS = np.array([0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30])


def test_ns_limits_and_forward_identity():
    c = NelsonSiegel(0.04, -0.02, 0.01, 2.0)
    assert float(c.zero(1e-9)) == pytest.approx(0.02, abs=1e-8)       # b0 + b1
    assert float(c.zero(1e4)) == pytest.approx(0.04, abs=1e-3)        # b0
    t = np.linspace(0.2, 30, 50)
    # analytic forward equals d/dt (t z)
    assert np.allclose(c.inst_forward(t), super(NelsonSiegel, c).inst_forward(t), atol=1e-7)
    assert np.allclose(TRUE.inst_forward(t), super(Svensson, TRUE).inst_forward(t), atol=1e-7)


def test_par_bond_on_curve_prices_at_par():
    for T in (2.0, 7.5, 30.0):
        c = TRUE.par_yield(T, 2)
        from firv.instruments import CMBond
        assert CMBond(T, c, 2, "g").pv({"g": TRUE}) == pytest.approx(1.0, abs=1e-12)


def test_bootstrap_reprices_inputs():
    par = TRUE.par_yield_grid(TENORS, 2)
    boot = bootstrap_par(TENORS, par, 2)
    got = np.array([boot.par_yield(float(t), 2) for t in TENORS])
    assert np.max(np.abs(got - par)) * 1e4 < 0.01
    # and the bootstrapped zeros are close to the true ones (interpolation error only)
    assert np.max(np.abs(boot.zero(TENORS) - TRUE.zero(TENORS))) * 1e4 < 1.5


@pytest.mark.parametrize("kind", ["zero", "par"])
def test_nss_recovers_known_curve(kind):
    vals = TRUE.zero(TENORS) if kind == "zero" else TRUE.par_yield_grid(TENORS, 2)
    res = fit("nss", CurveData(TENORS, vals, kind=kind, freq=2))
    assert res.rmse_bp < 0.05
    grid = np.linspace(0.5, 30, 60)
    assert np.max(np.abs(res.curve.zero(grid) - TRUE.zero(grid))) * 1e4 < 1.0


def test_ns_fits_ns_data_exactly_and_spline_is_smooth():
    ns = NelsonSiegel(0.035, -0.01, 0.02, 1.8)
    res = fit("ns", CurveData(TENORS, ns.zero(TENORS), kind="zero"))
    assert res.rmse_bp < 0.01
    sp = fit("spline", CurveData(TENORS, ns.zero(TENORS), kind="zero"), lam=1e-4)
    assert sp.rmse_bp < 0.5
    rough = fit("spline", CurveData(TENORS, ns.zero(TENORS), kind="zero"), lam=100.0)
    assert rough.curve.roughness() < sp.curve.roughness()


def test_cubic_interpolates_and_loo_is_finite():
    d = CurveData(TENORS, TRUE.par_yield_grid(TENORS, 2), kind="par", freq=2)
    res = fit("cubic", d)
    assert res.rmse_bp < 1.0
    loo = leave_one_out("nss", d)
    assert np.isnan(loo[0]) and np.isnan(loo[-1]) and np.all(np.isfinite(loo[1:-1]))


def test_bond_fit_from_cash_flows():
    from firv.curves.fitting import BondObs, bond_ytm_from_dirty
    obs = []
    for T, cpn in [(1.3, 0.02), (2.6, 0.03), (4.1, 0.04), (5.9, 0.045), (8.2, 0.05), (10.4, 0.04),
                   (13.7, 0.05), (18.9, 0.055), (21.2, 0.05)]:
        times = np.arange(T % 1 or 1.0, T + 1e-9, 1.0)
        amounts = np.full(len(times), cpn * 100)
        amounts[-1] += 100
        dirty = float(np.sum(amounts * TRUE.df(times)))
        b = BondObs(times, amounts, dirty, 0.0, 1, times[0])
        b.ytm = bond_ytm_from_dirty(b, dirty)
        obs.append(b)
    d = CurveData([o.maturity for o in obs], [o.ytm for o in obs], kind="bond", freq=1, bonds=obs)
    res = fit("nss", d)
    assert res.rmse_bp < 0.2
    assert abs(float(res.curve.zero(10.0) - TRUE.zero(10.0))) * 1e4 < 2.0


def test_zero_curve_interpolations_agree_at_nodes():
    z = TRUE.zero(TENORS)
    for interp in ("linear", "loglinear", "cubic", "pchip"):
        c = ZeroCurve(TENORS, z, interp)
        assert np.allclose(c.zero(TENORS), z, atol=1e-12)


def test_changes_never_span_a_data_gap():
    from firv.curves.pca import changes_bp
    idx = pd.bdate_range("2001-01-01", periods=300)
    df = pd.DataFrame({1.0: np.linspace(5, 6, 300), 30.0: np.linspace(6, 7, 300)}, index=idx)
    df.iloc[100:250, 1] = np.nan          # the long tenor disappears for a while (like the US 30y)
    df.iloc[250:, :] += 3.0               # a level shift happens during the gap
    ch = changes_bp(df)
    assert ch.abs().max().max() < 50      # the 300 bp move across the gap is not a "daily change"
    assert len(ch) == 299 - 151           # 99 changes before the gap, 149 after it


def test_pca_recovers_planted_factors():
    rng = np.random.default_rng(0)
    tenors = np.array([1, 2, 3, 5, 7, 10, 20, 30.0])
    level = np.ones_like(tenors) / np.sqrt(len(tenors))
    slope = np.log(tenors) - np.log(tenors).mean()
    slope /= np.linalg.norm(slope)
    n = 3000
    f = rng.normal(size=(n, 2)) * np.array([8.0, 3.0])
    noise = rng.normal(size=(n, len(tenors))) * 0.3
    changes = f @ np.vstack([level, slope]) + noise          # bp
    levels = pd.DataFrame(np.cumsum(changes, axis=0) / 100.0, columns=tenors)
    r = pca_changes(levels, k=3)
    assert abs(r.loadings[:, 0] @ level) > 0.99
    assert abs(r.loadings[:, 1] @ slope) > 0.98
    assert r.loadings[:, 1][-1] > r.loadings[:, 1][0]          # sign: steepening
    assert r.explained[0] > 0.8
    dec = decompose_move(levels, levels.index[0], levels.index[-1], r)
    total = sum(dec["contrib"].values()) + dec["residual"]
    assert np.allclose(total, dec["change"])
