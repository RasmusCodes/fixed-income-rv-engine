"""Dated fixed-rate bonds: cash flows, accrued interest, street-convention yields and
yield-based risk (modified duration, convexity, DV01).

Yields use the ICMA street convention: with w the fraction of the current coupon period
left until the next coupon and f the coupon frequency,

    dirty = sum_k CF_k / (1 + y/f)^(k - 1 + w).

Zero-coupon bonds (Polish OK bonds) use the same formula with f = 1, which equals
(100/P)^(1/T) - 1 with T in ACT/ACT periods.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq

from .curves.base import Curve
from .curves.fitting import BondObs
from .dates import accrual_fraction, add_months, coupon_schedule, previous_coupon, year_fraction


@dataclass(frozen=True)
class Bond:
    maturity: dt.date
    coupon: float                 # annual coupon rate, decimal
    frequency: int = 1
    basis: str = "ACT/ACT ICMA"
    face: float = 100.0
    name: str = ""
    eom: bool = False

    # ---- schedule -------------------------------------------------------------------
    def coupon_dates(self, settle: dt.date) -> list[dt.date]:
        return coupon_schedule(self.maturity, self.frequency, start=settle, eom=self.eom)

    def prev_next(self, settle: dt.date):
        nxt = self.coupon_dates(settle)[0]
        prv = add_months(nxt, -12 // self.frequency, eom=self.eom)
        return prv, nxt

    def accrued(self, settle: dt.date) -> float:
        if self.coupon == 0.0:
            return 0.0
        prv, nxt = self.prev_next(settle)
        return self.face * self.coupon / self.frequency * accrual_fraction(prv, nxt, settle, self.basis)

    def cashflows(self, settle: dt.date):
        dates = self.coupon_dates(settle)
        amounts = np.full(len(dates), self.face * self.coupon / self.frequency)
        amounts[-1] += self.face
        return dates, amounts

    def _w(self, settle: dt.date) -> float:
        prv, nxt = self.prev_next(settle)
        return (nxt - settle).days / (nxt - prv).days

    # ---- yield conventions ---------------------------------------------------------------
    def dirty_from_yield(self, y: float, settle: dt.date) -> float:
        _, amounts = self.cashflows(settle)
        expo = np.arange(len(amounts)) + self._w(settle)
        return float(np.sum(amounts / (1.0 + y / self.frequency) ** expo))

    def clean_from_yield(self, y: float, settle: dt.date) -> float:
        return self.dirty_from_yield(y, settle) - self.accrued(settle)

    def yield_from_clean(self, clean: float, settle: dt.date) -> float:
        dirty = clean + self.accrued(settle)
        return brentq(lambda y: self.dirty_from_yield(y, settle) - dirty, -0.5, 2.0, xtol=1e-12)

    def risk(self, y: float, settle: dt.date) -> dict:
        """Yield-based analytics per 100 face: dirty price, Macaulay and modified duration,
        convexity, DV01 (price gain for a 1 bp yield fall)."""
        _, amounts = self.cashflows(settle)
        f = self.frequency
        expo = np.arange(len(amounts)) + self._w(settle)
        v = (1.0 + y / f) ** (-expo)
        pv = amounts * v
        dirty = float(pv.sum())
        mac = float(np.sum(pv * expo) / dirty) / f
        mod = mac / (1.0 + y / f)
        conv = float(np.sum(pv * expo * (expo + 1))) / (dirty * f * f * (1.0 + y / f) ** 2)
        return {"dirty": dirty, "macaulay": mac, "modified": mod, "convexity": conv,
                "dv01": mod * dirty * 1e-4}

    # ---- curve pricing -----------------------------------------------------------------
    def times(self, settle: dt.date) -> np.ndarray:
        dates, _ = self.cashflows(settle)
        return np.array([year_fraction(settle, d, "ACT/365F") for d in dates])

    def dirty_from_curve(self, curve: Curve, settle: dt.date, z_spread: float = 0.0) -> float:
        t = self.times(settle)
        _, amounts = self.cashflows(settle)
        return float(np.sum(amounts * np.exp(-(curve.zero(t) + z_spread) * t)))

    def z_spread(self, curve: Curve, settle: dt.date, clean: float) -> float:
        dirty = clean + self.accrued(settle)
        return brentq(lambda s: self.dirty_from_curve(curve, settle, s) - dirty, -0.2, 0.5, xtol=1e-12)

    def to_obs(self, settle: dt.date, clean: float, ytm: float | None = None) -> BondObs:
        """Package for curve fitting (cash-flow times, amounts, dirty price, market yield)."""
        dates, amounts = self.cashflows(settle)
        y = self.yield_from_clean(clean, settle) if ytm is None else ytm
        return BondObs(self.times(settle), amounts, clean + self.accrued(settle), y,
                       self.frequency, self._w(settle), self.name)


def implied_coupon(maturity: dt.date, settle: dt.date, clean: float, ytm: float,
                   frequency: int = 1, basis: str = "ACT/ACT ICMA", eom: bool = False) -> float:
    """Coupon rate that makes (clean price, yield) consistent. Price is linear in the
    coupon at a fixed yield, so two evaluations give it exactly."""
    b0 = Bond(maturity, 0.0, frequency, basis, eom=eom)
    b1 = Bond(maturity, 0.01, frequency, basis, eom=eom)
    p0 = b0.clean_from_yield(ytm, settle)
    p1 = b1.clean_from_yield(ytm, settle)
    return 0.01 * (clean - p0) / (p1 - p0)


def business_days_after(d: dt.date, n: int, holidays: set | None = None) -> dt.date:
    """Settlement date n business days after d (weekends and given holidays skipped)."""
    holidays = holidays or set()
    out, k = d, 0
    while k < n:
        out += dt.timedelta(days=1)
        if out.weekday() < 5 and out not in holidays:
            k += 1
    return out
