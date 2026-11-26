"""Nelson-Siegel (1987) and Nelson-Siegel-Svensson (Svensson 1994) curves.

Zero rates are continuously compounded:

    NS : z(t) = b0 + b1*L1(t/tau) + b2*L2(t/tau)
    NSS: z(t) = NS + b3*L2(t/tau2)

with L1(x) = (1-exp(-x))/x and L2(x) = L1(x) - exp(-x). The instantaneous forward is
f(t) = b0 + b1*exp(-t/tau) + b2*(t/tau)*exp(-t/tau) [+ b3*(t/tau2)*exp(-t/tau2)].
This is the parameterisation used by the Fed (Gurkaynak, Sack and Wright 2007), the ECB
and the Bundesbank, so published parameters plug in directly.
"""
from __future__ import annotations

import numpy as np

from .base import Curve, as_array


def _l1(x):
    x = np.asarray(x, float)
    small = np.abs(x) < 1e-8
    xs = np.where(small, 1.0, x)
    return np.where(small, 1.0 - x / 2.0, (1.0 - np.exp(-xs)) / xs)


def _l2(x):
    x = np.asarray(x, float)
    return _l1(x) - np.exp(-x)


def ns_loadings(t, tau):
    """Design matrix [1, L1, L2] at maturities t (zero-rate loadings)."""
    t = as_array(t)
    x = t / tau
    return np.column_stack([np.ones_like(t), _l1(x), _l2(x)])


def nss_loadings(t, tau1, tau2):
    t = as_array(t)
    return np.column_stack([ns_loadings(t, tau1), _l2(t / tau2)])


class NelsonSiegel(Curve):
    label = "Nelson-Siegel"
    n_params = 4

    def __init__(self, b0, b1, b2, tau):
        self.b0, self.b1, self.b2, self.tau = float(b0), float(b1), float(b2), float(tau)

    @property
    def params(self):
        return np.array([self.b0, self.b1, self.b2, self.tau])

    @classmethod
    def from_params(cls, p):
        return cls(*p)

    def zero(self, t):
        t = as_array(t)
        x = t / self.tau
        return self.b0 + self.b1 * _l1(x) + self.b2 * _l2(x)

    def inst_forward(self, t, h=None):
        t = as_array(t)
        e = np.exp(-t / self.tau)
        return self.b0 + self.b1 * e + self.b2 * (t / self.tau) * e

    def __repr__(self):
        return (f"NelsonSiegel(b0={self.b0:.5f}, b1={self.b1:.5f}, b2={self.b2:.5f}, "
                f"tau={self.tau:.3f})")


class Svensson(Curve):
    label = "Nelson-Siegel-Svensson"
    n_params = 6

    def __init__(self, b0, b1, b2, b3, tau1, tau2):
        self.b0, self.b1, self.b2, self.b3 = float(b0), float(b1), float(b2), float(b3)
        self.tau1, self.tau2 = float(tau1), float(tau2)

    @property
    def params(self):
        return np.array([self.b0, self.b1, self.b2, self.b3, self.tau1, self.tau2])

    @classmethod
    def from_params(cls, p):
        return cls(*p)

    def zero(self, t):
        t = as_array(t)
        x1, x2 = t / self.tau1, t / self.tau2
        return self.b0 + self.b1 * _l1(x1) + self.b2 * _l2(x1) + self.b3 * _l2(x2)

    def inst_forward(self, t, h=None):
        t = as_array(t)
        e1, e2 = np.exp(-t / self.tau1), np.exp(-t / self.tau2)
        return (self.b0 + self.b1 * e1 + self.b2 * (t / self.tau1) * e1
                + self.b3 * (t / self.tau2) * e2)

    def __repr__(self):
        return (f"Svensson(b0={self.b0:.5f}, b1={self.b1:.5f}, b2={self.b2:.5f}, "
                f"b3={self.b3:.5f}, tau1={self.tau1:.3f}, tau2={self.tau2:.3f})")
