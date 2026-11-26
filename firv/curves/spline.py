"""Spline curves.

Two spline families:

* ``ZeroCurve(..., interp='cubic')`` in :mod:`firv.curves.base` - a natural cubic spline
  through zero rates. It reproduces every input exactly, so its fitting error can only be
  judged out of sample (leave-one-out), which :mod:`firv.curves.fitting` does.
* :class:`ForwardSpline` - a smoothing spline: the instantaneous forward curve is a cubic
  B-spline and the fit minimises squared pricing errors plus lambda * integral f''(t)^2,
  the roughness penalty of the variable roughness penalty (VRP) family used by the Bank
  of England (Anderson and Sleath 2001) and Waggoner (1997). Beyond the last knot the
  forward is held flat.
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import BSpline

from .base import Curve, as_array

DEFAULT_KNOTS = (0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0, 40.0)


def make_knot_vector(breaks, k: int = 3):
    b = np.asarray(sorted(set(float(x) for x in breaks)))
    return np.concatenate([np.repeat(b[0], k), b, np.repeat(b[-1], k)])


class ForwardSplineBasis:
    """Cubic B-spline basis for the forward curve with cached integrals and penalty."""

    def __init__(self, breaks=DEFAULT_KNOTS, k: int = 3):
        self.k = k
        self.knots = make_knot_vector(breaks, k)
        self.n = len(self.knots) - k - 1
        self.t_max = float(self.knots[-1])
        self.basis = []
        for j in range(self.n):
            c = np.zeros(self.n)
            c[j] = 1.0
            self.basis.append(BSpline(self.knots, c, k, extrapolate=False))
        self.anti = [b.antiderivative() for b in self.basis]
        self.penalty = self._penalty_matrix()

    def _penalty_matrix(self):
        # Integral of B_i'' B_j'' over [0, t_max] by Gauss-Legendre on each knot interval.
        xs, ws = np.polynomial.legendre.leggauss(8)
        brk = np.unique(self.knots)
        second = [b.derivative(2) for b in self.basis]
        omega = np.zeros((self.n, self.n))
        for a, b in zip(brk[:-1], brk[1:]):
            x = 0.5 * (b - a) * xs + 0.5 * (a + b)
            w = 0.5 * (b - a) * ws
            vals = np.array([np.nan_to_num(s(x)) for s in second])
            omega += (vals * w) @ vals.T
        return omega

    def values(self, t):
        """B_j(t) with flat extension beyond t_max; shape (len(t), n)."""
        t = np.clip(as_array(t), 0.0, self.t_max)
        return np.column_stack([np.nan_to_num(b(t)) for b in self.basis])

    def integrals(self, t):
        """I_j(t) = integral_0^t B_j(s) ds, with the forward held flat beyond t_max."""
        t = as_array(t)
        tc = np.clip(t, 0.0, self.t_max)
        base = np.column_stack([np.nan_to_num(a(tc)) - np.nan_to_num(a(0.0)) for a in self.anti])
        extra = np.clip(t - self.t_max, 0.0, None)
        if np.any(extra > 0):
            base = base + extra[:, None] * self.values(np.full_like(t, self.t_max))
        return base


class ForwardSpline(Curve):
    label = "Smoothing spline"

    def __init__(self, basis: ForwardSplineBasis, coefs):
        self.basis_obj = basis
        self.coefs = np.asarray(coefs, float)

    def zero(self, t):
        t = as_array(t)
        flat = np.atleast_1d(t)
        tt = np.maximum(flat, 1e-6)
        z = (self.basis_obj.integrals(tt) @ self.coefs) / tt
        return z.reshape(t.shape) if t.ndim else float(z[0])

    def inst_forward(self, t, h=None):
        t = as_array(t)
        flat = np.atleast_1d(t)
        f = self.basis_obj.values(flat) @ self.coefs
        return f.reshape(t.shape) if t.ndim else float(f[0])

    def roughness(self):
        return float(self.coefs @ self.basis_obj.penalty @ self.coefs)
