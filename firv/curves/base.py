"""Curve objects.

Every curve exposes continuously compounded zero rates ``zero(t)`` (decimal, t in years);
discount factors, forwards and par yields follow from that. Curves are immutable: shifts
and key-rate bumps return new curve objects, which is how all risk numbers are computed
(full revaluation, no duration shortcuts).
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline, PchipInterpolator

_EPS_T = 1e-6


def as_array(t):
    return np.asarray(t, dtype=float)


class Curve:
    """Base class. Subclasses implement :meth:`zero`."""

    label = "curve"

    def zero(self, t):  # pragma: no cover - abstract
        raise NotImplementedError

    # ---- derived quantities -------------------------------------------------------
    def df(self, t):
        t = as_array(t)
        return np.exp(-self.zero(t) * t)

    def zero_compounded(self, t, freq: int = 1):
        """Zero rate with ``freq`` compounding periods per year (freq=0: continuous)."""
        z = self.zero(t)
        return z if freq == 0 else freq * (np.exp(z / freq) - 1.0)

    def forward(self, t1, t2):
        """Continuously compounded forward rate between t1 and t2."""
        t1, t2 = as_array(t1), as_array(t2)
        return (self.zero(t2) * t2 - self.zero(t1) * t1) / np.maximum(t2 - t1, _EPS_T)

    def forward_simple(self, t1, t2):
        """Simply compounded forward rate (money-market style) between t1 and t2."""
        t1, t2 = as_array(t1), as_array(t2)
        return (self.df(t1) / self.df(t2) - 1.0) / np.maximum(t2 - t1, _EPS_T)

    def inst_forward(self, t, h: float = 1e-4):
        """Instantaneous forward f(t) = d/dt [t z(t)] (numerical unless overridden)."""
        t = as_array(t)
        lo = np.maximum(t - h, 0.0)
        hi = t + h
        return (self.zero(hi) * hi - self.zero(lo) * lo) / (hi - lo)

    def annuity(self, T: float, freq: int = 2, start: float = 0.0):
        """Sum of accrual-weighted discount factors for coupons on a regular grid ending at
        T (spot or forward starting at ``start``). A short first period accrues pro rata."""
        times, accr = coupon_grid(T, freq, start)
        return float(np.sum(accr * self.df(times))) / freq

    def par_yield(self, T, freq: int = 2, start: float = 0.0):
        """Par yield (coupon rate, compounding ``freq``) of a bullet bond maturing at T.

        For maturities of one coupon period or less the instrument is a single payment and
        the money-market (simple) yield is returned, the convention for bills."""
        T_arr = np.atleast_1d(as_array(T))
        out = np.empty_like(T_arr)
        for i, Ti in enumerate(T_arr):
            if Ti - start <= 1.0 / freq + 1e-9:
                out[i] = float(self.forward_simple(start, Ti))
            else:
                ann = self.annuity(Ti, freq, start)
                out[i] = (float(self.df(start)) - float(self.df(Ti))) / ann
        return out if np.ndim(T) else float(out[0])

    def par_yield_grid(self, tenors, freq: int = 2):
        return np.array([self.par_yield(float(t), freq) for t in tenors])

    # ---- transformations -------------------------------------------------------------
    def shifted(self, shift):
        """Parallel shift (decimal) or a function of t added to zero rates."""
        fn = shift if callable(shift) else (lambda t, s=float(shift): np.full_like(as_array(t), s))
        return ShiftedCurve(self, fn)

    def key_rate_bumped(self, key_tenors, bumps):
        """Zero curve plus a piecewise-linear bump through (key_tenors, bumps) - the
        triangular key-rate shape of Ho (1992); flat beyond the first and last key."""
        k = np.asarray(key_tenors, float)
        b = np.asarray(bumps, float)
        return ShiftedCurve(self, lambda t: np.interp(as_array(t), k, b))

    def rolled(self, h: float):
        """The curve as seen h years later if the curve is unchanged ("roll-down" world):
        the same function of time-to-maturity."""
        return self

    def sample(self, tenors):
        return {float(t): float(self.zero(float(t))) for t in tenors}


def coupon_grid(T: float, freq: int, start: float = 0.0):
    """Coupon times (years) of a bullet maturing at T with frequency ``freq`` from ``start``
    and the accrual fraction of each period (1 except a short first period)."""
    step = 1.0 / freq
    times = []
    t = T
    while t > start + 1e-9:
        times.append(t)
        t -= step
    times = np.array(times[::-1])
    accr = np.ones_like(times)
    first_len = times[0] - start
    accr[0] = min(first_len / step, 1.0)
    return times, accr


class ShiftedCurve(Curve):
    label = "shifted"

    def __init__(self, base: Curve, fn):
        self.base, self.fn = base, fn

    def zero(self, t):
        t = as_array(t)
        return self.base.zero(t) + self.fn(t)


class ZeroCurve(Curve):
    """Interpolated continuously compounded zero curve.

    interp: 'linear' (zero rates), 'loglinear' (log discount factors = piecewise flat
    forwards), 'cubic' (natural cubic spline on zero rates) or 'pchip' (monotone cubic).
    Flat zero-rate extrapolation outside the nodes.
    """

    label = "zero"

    def __init__(self, tenors, zeros, interp: str = "linear"):
        t = np.asarray(tenors, float)
        z = np.asarray(zeros, float)
        order = np.argsort(t)
        self.t, self.z, self.interp = t[order], z[order], interp
        if interp == "cubic":
            self._f = CubicSpline(self.t, self.z, bc_type="natural")
        elif interp == "pchip":
            self._f = PchipInterpolator(self.t, self.z)
        elif interp in ("linear", "loglinear"):
            self._f = None
        else:
            raise ValueError(f"unknown interpolation {interp!r}")

    def zero(self, t):
        t = as_array(t)
        tc = np.clip(t, self.t[0], self.t[-1])
        if self.interp == "linear":
            z = np.interp(tc, self.t, self.z)
        elif self.interp == "loglinear":
            lndf = np.interp(tc, self.t, -self.z * self.t)
            z = -lndf / np.maximum(tc, _EPS_T)
            z = np.where(tc <= self.t[0], self.z[0], z)
        else:
            z = self._f(tc)
        return z


class FunctionCurve(Curve):
    label = "function"

    def __init__(self, fn, label: str = "function"):
        self.fn, self.label = fn, label

    def zero(self, t):
        return self.fn(as_array(t))
