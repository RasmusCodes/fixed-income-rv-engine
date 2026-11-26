"""Instruments on a time-to-maturity grid, priced off named curves.

These are what trades are built from. Each instrument knows which curve(s) it is priced
on (``curve`` key into a dict of curves) and can be aged by h years, which is how carry
and roll-down are computed: value today, value after h years on the same curves, plus the
cash paid in between.

* :class:`CMBond` - fixed-coupon government bond (a constant-maturity point when the
  coupon equals today's par yield).
* :class:`Swap` - vanilla fixed-for-floating swap, single curve (OIS discounting); value
  to the fixed-rate receiver.
* :class:`Linker` - inflation-linked bond priced on a real curve, quoted in real terms
  (index ratio 1 today).
* :class:`CreditBond` - fixed-coupon bond priced at a z-spread over a government curve.
* :class:`BondFuture` - deliverable bond futures contract approximated by its
  cheapest-to-deliver: forward price / conversion factor.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from .curves.base import Curve, coupon_grid


def street_dv01(times, amounts, freq: int, dirty: float) -> float:
    """DV01 per unit notional with respect to the instrument's own yield to maturity
    (street convention: compounding ``freq``, exponents t*freq periods): the value gain
    for a 1 bp fall in that yield. This is the DV01 traders quote and size trades with."""
    from scipy.optimize import brentq
    if not len(times):
        return 0.0
    expo = np.asarray(times) * freq
    amounts = np.asarray(amounts)

    def price(y):
        return float(np.sum(amounts / (1 + y / freq) ** expo))

    y = brentq(lambda yy: price(yy) - dirty, -0.5, 2.0, xtol=1e-14)
    return float(np.sum(amounts * (expo / freq) * (1 + y / freq) ** (-expo - 1))) * 1e-4


def _bond_flows(T: float, coupon: float, freq: int):
    if T <= 1e-9:
        return np.array([]), np.array([]), 0.0
    times, accr = coupon_grid(T, freq)
    amounts = np.full(len(times), coupon / freq)
    amounts[-1] += 1.0
    accrued = coupon / freq * (1.0 - accr[0])     # part of the current period already run
    return times, amounts, accrued


@dataclass(frozen=True)
class CMBond:
    T: float
    coupon: float
    freq: int = 2
    curve: str = "gov"
    label: str = ""

    kind = "bond"

    def flows(self):
        return _bond_flows(self.T, self.coupon, self.freq)

    def pv(self, curves: dict, spread: float = 0.0) -> float:
        times, amounts, _ = self.flows()
        if not len(times):
            return 0.0
        c: Curve = curves[self.curve]
        return float(np.sum(amounts * np.exp(-(c.zero(times) + spread) * times)))

    def accrued(self) -> float:
        return self.flows()[2]

    def aged(self, h: float):
        return replace(self, T=max(self.T - h, 0.0))

    def cash_in(self, h: float) -> float:
        times, amounts, _ = self.flows()
        return float(amounts[times <= h + 1e-9].sum())

    def yield_dv01(self, curves: dict) -> float:
        times, amounts, _ = self.flows()
        return street_dv01(times, amounts, self.freq, self.pv(curves))

    def ytm(self, curves: dict) -> float:
        """Yield to maturity (compounding freq) of the curve-implied dirty price."""
        from scipy.optimize import brentq
        times, amounts, _ = self.flows()
        dirty = self.pv(curves)
        expo = times * self.freq
        return brentq(lambda y: float(np.sum(amounts / (1 + y / self.freq) ** expo)) - dirty,
                      -0.5, 2.0, xtol=1e-12)


@dataclass(frozen=True)
class Swap:
    T: float
    fixed_rate: float
    freq: int = 1
    curve: str = "swap"
    label: str = ""

    kind = "swap"

    def pv(self, curves: dict, spread: float = 0.0) -> float:
        """Receiver value per unit notional: fixed leg minus floating leg (at par)."""
        if self.T <= 1e-9:
            return 0.0
        c: Curve = curves[self.curve]
        times, accr = coupon_grid(self.T, self.freq)
        df = np.exp(-(c.zero(times) + spread) * times)
        fixed = self.fixed_rate / self.freq * float(np.sum(accr * df))
        floating = 1.0 - float(df[-1])
        return fixed - floating

    def aged(self, h: float):
        return replace(self, T=max(self.T - h, 0.0))

    def cash_in(self, h: float) -> float:
        # net fixed coupons minus the floating fixings received over h, approximated by
        # the fixed coupons only; the floating leg's carry is booked through financing
        times, accr = coupon_grid(self.T, self.freq) if self.T > 0 else (np.array([]), np.array([]))
        return float((self.fixed_rate / self.freq * accr)[times <= h + 1e-9].sum())

    def par_rate(self, curves: dict) -> float:
        return curves[self.curve].par_yield(self.T, self.freq)

    def yield_dv01(self, curves: dict) -> float:
        """PV01: value gain for the receiver when the par swap rate falls 1 bp (the
        annuity times 1 bp)."""
        if self.T <= 1e-9:
            return 0.0
        return curves[self.curve].annuity(self.T, self.freq) * 1e-4


@dataclass(frozen=True)
class Linker:
    """Inflation-linked bond in real terms on a real (zero) curve. A 1 bp fall in real
    yields is worth its real DV01; breakevens = nominal minus real zero rates."""

    T: float
    real_coupon: float
    freq: int = 2
    curve: str = "real"
    label: str = ""

    kind = "linker"

    def pv(self, curves: dict, spread: float = 0.0) -> float:
        times, amounts, _ = _bond_flows(self.T, self.real_coupon, self.freq)
        if not len(times):
            return 0.0
        c: Curve = curves[self.curve]
        return float(np.sum(amounts * np.exp(-(c.zero(times) + spread) * times)))

    def aged(self, h: float):
        return replace(self, T=max(self.T - h, 0.0))

    def cash_in(self, h: float) -> float:
        times, amounts, _ = _bond_flows(self.T, self.real_coupon, self.freq)
        return float(amounts[times <= h + 1e-9].sum())

    def yield_dv01(self, curves: dict) -> float:
        times, amounts, _ = _bond_flows(self.T, self.real_coupon, self.freq)
        return street_dv01(times, amounts, self.freq, self.pv(curves))


@dataclass(frozen=True)
class CreditBond:
    T: float
    coupon: float
    z_spread: float
    freq: int = 2
    curve: str = "gov"
    label: str = ""

    kind = "credit"

    def pv(self, curves: dict, spread: float = 0.0) -> float:
        times, amounts, _ = _bond_flows(self.T, self.coupon, self.freq)
        if not len(times):
            return 0.0
        c: Curve = curves[self.curve]
        s = self.z_spread + spread
        return float(np.sum(amounts * np.exp(-(c.zero(times) + s) * times)))

    def with_spread(self, s: float):
        return replace(self, z_spread=s)

    def aged(self, h: float):
        return replace(self, T=max(self.T - h, 0.0))

    def cash_in(self, h: float) -> float:
        times, amounts, _ = _bond_flows(self.T, self.coupon, self.freq)
        return float(amounts[times <= h + 1e-9].sum())

    def yield_dv01(self, curves: dict) -> float:
        times, amounts, _ = _bond_flows(self.T, self.coupon, self.freq)
        return street_dv01(times, amounts, self.freq, self.pv(curves))


@dataclass(frozen=True)
class BondFuture:
    """Bond future approximated by one deliverable (the CTD): fair price = (forward dirty
    price of the CTD at delivery minus accrued at delivery) / conversion factor. P&L per
    unit of contract notional is the change in that price; there is no upfront value."""

    ctd: CMBond
    conversion_factor: float
    delivery: float                # years to delivery
    repo_curve: str = "repo"
    label: str = ""

    kind = "future"

    @property
    def curve(self):
        return self.ctd.curve

    def fair_price(self, curves: dict) -> float:
        spot_dirty = self.ctd.pv(curves)
        h = self.delivery
        r = float(curves[self.repo_curve].zero(max(h, 1e-6))) if self.repo_curve in curves else \
            float(curves[self.ctd.curve].zero(max(h, 1e-6)))
        cpn_paid = self.ctd.cash_in(h)
        fwd_dirty = spot_dirty * np.exp(r * h) - cpn_paid           # coupons not reinvested
        fwd_clean = fwd_dirty - self.ctd.aged(h).accrued()
        return fwd_clean / self.conversion_factor

    def pv(self, curves: dict, spread: float = 0.0) -> float:
        # marked-to-market value relative to an entry at today's fair price is handled by
        # risk functions through price differences; pv returns the price itself
        return self.fair_price(curves)

    def aged(self, h: float):
        return replace(self, ctd=self.ctd.aged(h), delivery=max(self.delivery - h, 0.0))

    def cash_in(self, h: float) -> float:
        return 0.0

    def yield_dv01(self, curves: dict) -> float:
        """Futures DV01 per unit of contract face: CTD DV01 / conversion factor."""
        return self.ctd.yield_dv01(curves) / self.conversion_factor


def par_bond(curves: dict, curve: str, T: float, freq: int = 2, label: str = "") -> CMBond:
    """A bond priced at par on today's curve: its coupon is the curve's par yield."""
    c = curves[curve].par_yield(T, freq)
    return CMBond(T=T, coupon=float(c), freq=freq, curve=curve, label=label or f"{curve} {T:g}y")


def par_swap(curves: dict, curve: str, T: float, freq: int = 1, label: str = "") -> Swap:
    return Swap(T=T, fixed_rate=float(curves[curve].par_yield(T, freq)), freq=freq, curve=curve,
                label=label or f"{curve} swap {T:g}y")


def conversion_factor(coupon: float, years_to_maturity: float, months_extra: int = 0) -> float:
    """CBOT conversion factor of a US Treasury deliverable: the price per $1 at a 6% yield
    (semiannual) with maturity rounded down to whole quarters (notes/bonds), per the
    exchange formula. ``years_to_maturity`` is measured from the first day of the delivery
    month; ``months_extra`` the extra months (0, 3, 6, 9) beyond whole years after rounding
    down to the quarter."""
    n = int(years_to_maturity)
    v = months_extra if months_extra < 7 else months_extra - 6
    a = 1.0 / 1.03 ** (v / 6.0)
    b = coupon / 2.0 * (6 - v) / 6.0
    c = 1.0 / 1.03 ** (2 * n) if months_extra < 7 else 1.0 / 1.03 ** (2 * n + 1)
    d = coupon / 0.06 * (1.0 - c)
    return round(a * (coupon / 2.0 + c + d) - b, 4)
