"""Zero-coupon curve construction from par yields by bootstrapping.

Constant-maturity par yields (US Treasury CMT, French TEC, Japanese MoF yields) are
interpolated onto every coupon date with a monotone cubic (PCHIP), then discount factors are
solved one coupon date at a time:

    df(t_n) = (1 - c_n/f * sum_{i<n} df(t_i)) / (1 + c_n/f)

Tenors of one coupon period or less are money-market (simple) yields: df = 1/(1 + y*t).
The result is a :class:`~firv.curves.base.ZeroCurve` of continuously compounded zeros on
the coupon grid, so it reprices every input par bond exactly (up to interpolation).
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

from .base import ZeroCurve


def bootstrap_par(tenors, par_yields, freq: int = 2, interp: str = "loglinear") -> ZeroCurve:
    t = np.asarray(tenors, float)
    y = np.asarray(par_yields, float)
    order = np.argsort(t)
    t, y = t[order], y[order]
    step = 1.0 / freq
    nodes_t, nodes_df = [], []
    # money-market segment
    for ti, yi in zip(t, y):
        if ti <= step + 1e-9:
            nodes_t.append(ti)
            nodes_df.append(1.0 / (1.0 + yi * ti))
    coupon_t = t[t > step + 1e-9]
    if len(coupon_t):
        f_par = PchipInterpolator(t, y, extrapolate=True)
        n_max = int(round(coupon_t[-1] * freq))
        grid = np.arange(1, n_max + 1) * step
        # discount factor at one coupon period from the money-market segment or the par curve
        dfs = np.empty_like(grid)
        for n, tn in enumerate(grid):
            c = float(f_par(tn)) if tn >= t[0] else float(y[0])
            if n == 0:
                if nodes_t and abs(nodes_t[-1] - tn) < 1e-9:
                    dfs[n] = nodes_df[-1]
                    continue
                dfs[n] = 1.0 / (1.0 + c / freq)
            else:
                dfs[n] = (1.0 - c / freq * dfs[:n].sum()) / (1.0 + c / freq)
        for tn, dn in zip(grid, dfs):
            if not nodes_t or tn > nodes_t[-1] + 1e-9:
                nodes_t.append(tn)
                nodes_df.append(dn)
    nodes_t = np.asarray(nodes_t)
    nodes_df = np.asarray(nodes_df)
    zeros = -np.log(nodes_df) / nodes_t
    return ZeroCurve(nodes_t, zeros, interp=interp)
