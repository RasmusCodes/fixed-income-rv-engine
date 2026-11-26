import datetime as dt

import numpy as np
import pytest

from firv.bonds import Bond, business_days_after, implied_coupon
from firv.dates import add_months, coupon_schedule, year_fraction


def test_year_fractions():
    a, b = dt.date(2026, 1, 15), dt.date(2026, 7, 15)
    assert year_fraction(a, b, "ACT/365F") == pytest.approx(181 / 365)
    assert year_fraction(a, b, "ACT/360") == pytest.approx(181 / 360)
    assert year_fraction(a, b, "30/360") == pytest.approx(0.5)
    assert year_fraction(dt.date(2026, 1, 31), dt.date(2026, 2, 28), "30E/360") == pytest.approx(28 / 360)
    # ACT/ACT ISDA across a year end: 2023 (365 days) and 2024 (leap)
    yf = year_fraction(dt.date(2023, 12, 1), dt.date(2024, 2, 1), "ACT/ACT")
    assert yf == pytest.approx(31 / 365 + 31 / 366)


def test_add_months_and_schedule():
    assert add_months(dt.date(2026, 1, 31), 1) == dt.date(2026, 2, 28)
    assert add_months(dt.date(2026, 2, 28), 1, eom=True) == dt.date(2026, 3, 31)
    sched = coupon_schedule(dt.date(2030, 10, 25), 1, start=dt.date(2026, 11, 24))
    assert sched[0] == dt.date(2027, 10, 25) and sched[-1] == dt.date(2030, 10, 25) and len(sched) == 4


def test_par_bond_prices_at_par_on_coupon_date():
    b = Bond(dt.date(2036, 5, 15), 0.045, 2)
    settle = dt.date(2026, 5, 15)
    assert b.accrued(settle) == pytest.approx(0.0)
    assert b.clean_from_yield(0.045, settle) == pytest.approx(100.0, abs=1e-9)


def test_yield_price_round_trip_and_risk_against_finite_differences():
    b = Bond(dt.date(2035, 10, 25), 0.0575, 1)
    settle = dt.date(2026, 11, 24)
    y = 0.0612
    clean = b.clean_from_yield(y, settle)
    assert b.yield_from_clean(clean, settle) == pytest.approx(y, abs=1e-11)
    r = b.risk(y, settle)
    h = 1e-5
    up, dn = b.dirty_from_yield(y + h, settle), b.dirty_from_yield(y - h, settle)
    assert r["dv01"] == pytest.approx((dn - up) / (2 * h) * 1e-4, rel=1e-6)
    assert r["convexity"] == pytest.approx((up + dn - 2 * r["dirty"]) / (h * h) / r["dirty"], rel=1e-4)


def test_zero_coupon_yield_identity():
    # Polish OK bond: P = 100 / (1+y)^(periods) with ACT/ACT periods
    b = Bond(dt.date(2028, 1, 25), 0.0, 1)
    settle = dt.date(2026, 11, 24)
    y = b.yield_from_clean(95.41, settle)
    periods = 1 + (dt.date(2027, 1, 25) - settle).days / (dt.date(2027, 1, 25) - dt.date(2026, 1, 25)).days
    assert y == pytest.approx((100 / 95.41) ** (1 / periods) - 1, abs=1e-12)
    # the BondSpot fixing published 4.10% for OK0128 at 95.41 on 2026-11-20
    assert round(y * 100, 2) == 4.10


def test_implied_coupon_recovers_coupon():
    mat, settle = dt.date(2034, 10, 25), dt.date(2026, 11, 24)
    b = Bond(mat, 0.0475, 1)
    clean = b.clean_from_yield(0.0609, settle)
    assert implied_coupon(mat, settle, clean, 0.0609) == pytest.approx(0.0475, abs=1e-10)


def test_business_days():
    assert business_days_after(dt.date(2026, 11, 20), 2) == dt.date(2026, 11, 24)   # Fri -> Tue


def test_curve_pricing_matches_yield_pricing_on_flat_curve():
    from firv.curves import ZeroCurve
    b = Bond(dt.date(2031, 6, 30), 0.04, 2)
    settle = dt.date(2026, 6, 30)
    y = 0.05
    flat = ZeroCurve([0.1, 50], [2 * np.log1p(y / 2)] * 2)     # semiannual 5% as continuous
    assert b.dirty_from_curve(flat, settle) == pytest.approx(b.dirty_from_yield(y, settle), rel=2e-4)
