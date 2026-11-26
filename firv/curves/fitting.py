"""Curve fitting: one interface for every model and every kind of market data.

Observations come as :class:`CurveData`:

* ``kind='zero'``  continuously compounded zero rates (central bank curves, GSW, BoE);
* ``kind='par'``   par / constant-maturity yields with coupon frequency ``freq``
  (US CMT, French TEC, Japanese MoF yields);
* ``kind='bond'``  individual bonds with cash flows and dirty prices (Polish fixing).

Methods: ``ns`` (Nelson-Siegel), ``nss`` (Svensson), ``spline`` (smoothing forward
spline), ``cubic`` (natural cubic spline through zeros, an interpolant) and ``bootstrap``
(par yields only). Every fit reports residuals in basis points of the observed quantity
(zero rate, par yield, or yield to maturity), so errors are comparable across models.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import brentq, least_squares

from .base import Curve, ZeroCurve, coupon_grid
from .bootstrap import bootstrap_par
from .nelson_siegel import NelsonSiegel, Svensson, ns_loadings, nss_loadings
from .spline import DEFAULT_KNOTS, ForwardSpline, ForwardSplineBasis

METHODS = ("ns", "nss", "spline", "cubic", "bootstrap")


@dataclass
class BondObs:
    """One bond for curve fitting: cash-flow times (years from settlement), amounts per
    100 face, dirty price, and the market yield to maturity (decimal, compounding freq)."""

    times: np.ndarray
    amounts: np.ndarray
    dirty: float
    ytm: float
    freq: int = 1
    w_first: float = 1.0          # fraction of a period to the first cash flow
    name: str = ""

    @property
    def maturity(self) -> float:
        return float(self.times[-1])


@dataclass
class CurveData:
    tenors: np.ndarray
    values: np.ndarray            # decimals; zero (cont.), par (freq) or bond ytm
    kind: str = "par"
    freq: int = 2
    weights: np.ndarray | None = None
    bonds: list[BondObs] = field(default_factory=list)

    def __post_init__(self):
        self.tenors = np.asarray(self.tenors, float)
        self.values = np.asarray(self.values, float)
        if self.kind not in ("zero", "par", "bond"):
            raise ValueError(f"unknown data kind {self.kind!r}")
        if self.weights is None:
            self.weights = np.ones_like(self.tenors)

    def subset(self, mask):
        mask = np.asarray(mask, bool)
        return CurveData(self.tenors[mask], self.values[mask], self.kind, self.freq,
                         self.weights[mask], [b for b, m in zip(self.bonds, mask) if m]
                         if self.bonds else [])


@dataclass
class FitResult:
    method: str
    curve: Curve
    data: CurveData
    fitted: np.ndarray            # model values of the observed quantity (decimal)
    params: np.ndarray | None = None
    success: bool = True
    message: str = ""

    @property
    def residuals_bp(self) -> np.ndarray:
        return (self.fitted - self.data.values) * 1e4

    @property
    def rmse_bp(self) -> float:
        r = self.residuals_bp
        return float(np.sqrt(np.mean(r ** 2)))

    @property
    def max_abs_bp(self) -> float:
        return float(np.max(np.abs(self.residuals_bp)))


# ---------------------------------------------------------------------------- model values
class _ParPricer:
    """Vectorised par-yield evaluation for a fixed set of tenors."""

    def __init__(self, tenors, freq):
        self.tenors = np.asarray(tenors, float)
        self.freq = freq
        self.mm = self.tenors <= 1.0 / freq + 1e-9
        self.grids = []
        all_t, idx = [], []
        for i, T in enumerate(self.tenors):
            if self.mm[i]:
                continue
            times, accr = coupon_grid(float(T), freq)
            self.grids.append((i, len(all_t), len(times), accr))
            all_t.extend(times)
        self.all_t = np.asarray(all_t)

    def __call__(self, curve: Curve):
        out = np.empty_like(self.tenors)
        if self.mm.any():
            T = self.tenors[self.mm]
            out[self.mm] = (1.0 / curve.df(T) - 1.0) / T
        if len(self.all_t):
            dfs = curve.df(self.all_t)
            for i, start, n, accr in self.grids:
                d = dfs[start:start + n]
                out[i] = self.freq * (1.0 - d[-1]) / np.sum(accr * d)
        return out


def bond_dirty_from_curve(curve: Curve, bond: BondObs) -> float:
    return float(np.sum(bond.amounts * curve.df(bond.times)))


def bond_ytm_from_dirty(bond: BondObs, dirty: float) -> float:
    """Yield to maturity (compounding bond.freq) using the street convention exponents
    (k - 1 + w) in coupon periods."""
    n = len(bond.times)
    expo = np.arange(n) + bond.w_first

    def f(y):
        return float(np.sum(bond.amounts / (1.0 + y / bond.freq) ** expo)) - dirty

    return brentq(f, -0.5, 2.0, xtol=1e-12)


class _BondPricer:
    def __init__(self, bonds):
        self.bonds = bonds
        self.all_t = np.concatenate([b.times for b in bonds])
        self.slices = np.cumsum([0] + [len(b.times) for b in bonds])
        self.amounts = np.concatenate([b.amounts for b in bonds])
        self.dirty = np.array([b.dirty for b in bonds])
        # duration-based conversion of price errors into yield errors
        self.dur = np.array([_mod_duration(b) for b in bonds])

    def prices(self, curve: Curve):
        pv = self.amounts * curve.df(self.all_t)
        return np.add.reduceat(pv, self.slices[:-1])

    def yield_errors(self, curve: Curve):
        """First-order yield error (decimal): -(P_model - P_mkt) / (D_mod * P_mkt)."""
        return -(self.prices(curve) - self.dirty) / (self.dur * self.dirty)


def _mod_duration(b: BondObs) -> float:
    expo = np.arange(len(b.times)) + b.w_first
    disc = (1.0 + b.ytm / b.freq) ** (-expo)
    pv = b.amounts * disc
    mac = float(np.sum(pv * expo / b.freq) / np.sum(pv))
    return max(mac / (1.0 + b.ytm / b.freq), 1e-4)


def model_values(curve: Curve, data: CurveData, exact_bond_yields: bool = True) -> np.ndarray:
    if data.kind == "zero":
        return curve.zero(data.tenors)
    if data.kind == "par":
        return _ParPricer(data.tenors, data.freq)(curve)
    out = []
    for b in data.bonds:
        dirty = bond_dirty_from_curve(curve, b)
        out.append(bond_ytm_from_dirty(b, dirty) if exact_bond_yields
                   else b.ytm - (dirty - b.dirty) / (_mod_duration(b) * b.dirty))
    return np.asarray(out)


# ---------------------------------------------------------------------------- parametric fits
def _approx_zero(data: CurveData):
    """Rough continuously compounded zeros used to start nonlinear fits."""
    if data.kind == "zero":
        return data.tenors, data.values
    if data.kind == "par":
        y = data.values
        return data.tenors, data.freq * np.log1p(y / data.freq)
    t = np.array([b.maturity for b in data.bonds])
    y = np.array([b.ytm for b in data.bonds])
    f = data.bonds[0].freq if data.bonds else 1
    return t, f * np.log1p(y / f)


def _linear_betas(X, z, w):
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], z * sw, rcond=None)
    resid = X @ beta - z
    return beta, float(np.sum(w * resid ** 2))


TAU_GRID = np.exp(np.linspace(np.log(0.15), np.log(12.0), 28))


def _grid_ns(t, z, w):
    best = None
    for tau in TAU_GRID:
        beta, sse = _linear_betas(ns_loadings(t, tau), z, w)
        if best is None or sse < best[0]:
            best = (sse, np.r_[beta, tau])
    return best[1]


def _grid_nss(t, z, w, n_best: int = 3):
    cands = []
    for i, tau1 in enumerate(TAU_GRID):
        for tau2 in TAU_GRID[i + 2:]:
            beta, sse = _linear_betas(nss_loadings(t, tau1, tau2), z, w)
            cands.append((sse, np.r_[beta, tau1, tau2]))
    cands.sort(key=lambda c: c[0])
    return [c[1] for c in cands[:n_best]]


def _residual_fn(data: CurveData, make_curve):
    w = np.sqrt(data.weights)
    if data.kind == "zero":
        return lambda p: (make_curve(p).zero(data.tenors) - data.values) * w * 1e4
    if data.kind == "par":
        pricer = _ParPricer(data.tenors, data.freq)
        return lambda p: (pricer(make_curve(p)) - data.values) * w * 1e4
    pricer = _BondPricer(data.bonds)
    return lambda p: pricer.yield_errors(make_curve(p)) * w * 1e4


def _ns_from_x(x):
    return NelsonSiegel(x[0], x[1], x[2], np.exp(x[3]))


def _nss_from_x(x):
    tau1 = np.exp(x[4])
    return Svensson(x[0], x[1], x[2], x[3], tau1, tau1 + np.exp(x[5]))


def fit_ns(data: CurveData, x0=None, grid: bool = True) -> FitResult:
    t, z = _approx_zero(data)
    starts = [np.asarray(x0, float)] if x0 is not None else []
    if grid or not starts:
        starts.append(_grid_ns(t, z, data.weights))
    fn = _residual_fn(data, _ns_from_x)
    best = None
    for p in starts:
        x = np.r_[p[:3], np.log(max(p[3], 0.05))]
        try:
            res = least_squares(fn, x, method="lm" if len(t) > 4 else "trf", max_nfev=2000)
        except ValueError:
            res = least_squares(fn, x, max_nfev=2000)
        if best is None or res.cost < best.cost:
            best = res
    curve = _ns_from_x(best.x)
    return FitResult("ns", curve, data, model_values(curve, data), curve.params,
                     bool(best.success), str(best.message))


def fit_nss(data: CurveData, x0=None, grid: bool = True) -> FitResult:
    t, z = _approx_zero(data)
    starts = [np.asarray(x0, float)] if x0 is not None else []
    if grid or not starts:
        starts += _grid_nss(t, z, data.weights)
    fn = _residual_fn(data, _nss_from_x)
    lo = np.array([-1.0, -1.0, -1.0, -1.0, np.log(0.05), np.log(0.1)])
    hi = np.array([1.0, 1.0, 1.0, 1.0, np.log(30.0), np.log(40.0)])
    best = None
    for p in starts:
        tau1 = max(p[4], 0.05)
        gap = max(p[5] - tau1, 0.1)
        x = np.clip(np.r_[p[:4], np.log(tau1), np.log(gap)], lo + 1e-9, hi - 1e-9)
        res = least_squares(fn, x, bounds=(lo, hi), max_nfev=3000)
        if best is None or res.cost < best.cost:
            best = res
    curve = _nss_from_x(best.x)
    return FitResult("nss", curve, data, model_values(curve, data), curve.params,
                     bool(best.success), str(best.message))


# ---------------------------------------------------------------------------- splines
def _default_breaks(max_t: float):
    br = [k for k in DEFAULT_KNOTS if k < max_t - 1e-9]
    return br + [max(max_t, 1.0)]


_BASIS_CACHE: dict[tuple, ForwardSplineBasis] = {}


def spline_basis(max_t: float) -> ForwardSplineBasis:
    key = tuple(np.round(_default_breaks(max_t), 6))
    if key not in _BASIS_CACHE:
        _BASIS_CACHE[key] = ForwardSplineBasis(key)
    return _BASIS_CACHE[key]


def fit_spline(data: CurveData, lam: float = 0.05, basis: ForwardSplineBasis | None = None,
               c0=None) -> FitResult:
    """Smoothing forward spline.

    Minimises sum_i w_i e_i^2 + lam * integral f''(t)^2 dt with fit errors e_i and the
    forward f both in basis points, so ``lam`` is unit-free: lam = 0.05 charges one squared
    bp of fit error for every 20 bp^2/yr^3 of forward-curve roughness.
    """
    t, z = _approx_zero(data)
    basis = basis or spline_basis(float(np.max(t)))
    omega = basis.penalty
    # linear solve on the zero-rate proxy (exact for kind='zero'); bp^2 scaling cancels
    A = basis.integrals(np.maximum(t, 1e-6)) / np.maximum(t, 1e-6)[:, None]
    W = data.weights
    lhs = (A * W[:, None]).T @ A + lam * omega + 1e-12 * np.eye(basis.n)
    c = np.linalg.solve(lhs, (A * W[:, None]).T @ z) if c0 is None else np.asarray(c0, float)
    if data.kind != "zero":
        evals, evecs = np.linalg.eigh(omega)
        L = (evecs * np.sqrt(np.clip(evals, 0, None))).T        # omega = L^T L
        fn = _residual_fn(data, lambda cc: ForwardSpline(basis, cc))
        scale = np.sqrt(lam) * 1e4                             # penalty rows in bp

        def full(cc):
            return np.r_[fn(cc), scale * (L @ cc)]

        res = least_squares(full, c, method="trf", max_nfev=200)
        c = res.x
        ok, msg = bool(res.success), str(res.message)
    else:
        ok, msg = True, "linear solve"
    curve = ForwardSpline(basis, c)
    return FitResult("spline", curve, data, model_values(curve, data), c, ok, msg)


def fit_cubic(data: CurveData) -> FitResult:
    """Natural cubic spline through zero rates (bootstrapped from par yields if needed)."""
    if data.kind == "zero":
        curve = ZeroCurve(data.tenors, data.values, interp="cubic")
    elif data.kind == "par":
        boot = bootstrap_par(data.tenors, data.values, data.freq)
        curve = ZeroCurve(data.tenors, boot.zero(data.tenors), interp="cubic")
    else:
        t, z = _approx_zero(data)
        order = np.argsort(t)
        t, z = t[order], z[order]
        keep = np.r_[True, np.diff(t) > 1e-6]
        curve = ZeroCurve(t[keep], z[keep], interp="cubic")
    return FitResult("cubic", curve, data, model_values(curve, data))


def fit_bootstrap(data: CurveData) -> FitResult:
    if data.kind != "par":
        raise ValueError("bootstrap needs par yields")
    curve = bootstrap_par(data.tenors, data.values, data.freq)
    return FitResult("bootstrap", curve, data, model_values(curve, data))


def fit(method: str, data: CurveData, **kw) -> FitResult:
    m = method.lower()
    if m == "ns":
        return fit_ns(data, **kw)
    if m == "nss":
        return fit_nss(data, **kw)
    if m == "spline":
        return fit_spline(data, **kw)
    if m == "cubic":
        return fit_cubic(data)
    if m == "bootstrap":
        return fit_bootstrap(data)
    raise ValueError(f"unknown method {method!r}; choose from {METHODS}")


def leave_one_out(method: str, data: CurveData, interior_only: bool = True, **kw) -> np.ndarray:
    """Out-of-sample error (bp) at each observation when it is left out of the fit.

    With ``interior_only`` the shortest and longest points are skipped (their errors are
    extrapolation, not interpolation). Returns NaN for skipped points."""
    n = len(data.tenors) if data.kind != "bond" else len(data.bonds)
    t = data.tenors if data.kind != "bond" else np.array([b.maturity for b in data.bonds])
    out = np.full(n, np.nan)
    lo, hi = np.argmin(t), np.argmax(t)
    if method in ("ns", "nss") and "x0" not in kw:
        # warm start every leave-one-out fit from the full-sample fit (the left-out point
        # is not used again: least squares re-fits the remaining points from there)
        kw = dict(kw, x0=fit(method, data).curve.params, grid=False)
    for i in range(n):
        if interior_only and i in (lo, hi):
            continue
        mask = np.ones(n, bool)
        mask[i] = False
        res = fit(method, data.subset(mask), **kw)
        one = data.subset(~mask)
        out[i] = (model_values(res.curve, one)[0] - one.values[0]) * 1e4
    return out
