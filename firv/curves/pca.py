"""Principal components of yield-curve changes and historical curve decomposition.

PCA is run on changes (bp) of constant-maturity yields, so the components are the usual
level, slope and curvature shapes (Litterman and Scheinkman 1991). Signs are normalised:
PC1 loads positively on average (a rise in yields), PC2 rises with maturity (steepening),
PC3 is positive in the belly (the belly cheapening against the wings).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class PCAResult:
    tenors: np.ndarray
    loadings: np.ndarray            # n_tenors x k (unit-norm eigenvectors)
    eigenvalues: np.ndarray         # variance of each component (bp^2 per period)
    explained: np.ndarray           # share of total variance
    mean: np.ndarray                # mean change per tenor (bp)
    scores: pd.DataFrame | None = None
    start: object = None
    end: object = None
    n_obs: int = 0

    @property
    def vol_loadings(self) -> np.ndarray:
        """Loadings scaled to a one-standard-deviation move of each component (bp)."""
        return self.loadings * np.sqrt(self.eigenvalues)[None, :]

    def shock(self, k: int, n_sd: float = 1.0) -> np.ndarray:
        """Yield change (bp) at each tenor for an n_sd move in component k."""
        return self.vol_loadings[:, k] * n_sd

    def reconstruct(self, changes: np.ndarray, k: int = 3) -> np.ndarray:
        L = self.loadings[:, :k]
        f = (np.asarray(changes) - self.mean) @ L
        return self.mean + f @ L.T


def _normalise_signs(vecs: np.ndarray, tenors: np.ndarray) -> np.ndarray:
    v = vecs.copy()
    n = v.shape[1]
    if n >= 1 and v[:, 0].sum() < 0:
        v[:, 0] *= -1
    if n >= 2 and np.polyfit(np.log(tenors), v[:, 1], 1)[0] < 0:
        v[:, 1] *= -1
    if n >= 3:
        mid = (tenors > tenors.min() * 1.5) & (tenors < tenors.max() / 1.5)
        if mid.any() and v[mid, 2].mean() < 0:
            v[:, 2] *= -1
    return v


def changes_bp(levels: pd.DataFrame, diff: int = 1, max_gap_factor: float = 8.0) -> pd.DataFrame:
    """Changes (bp) between consecutive rows, computed BEFORE dropping incomplete rows so a
    change never spans a data gap (e.g. the US 30y CMT was not published Feb 2002 - Feb
    2006); changes over more than ``max_gap_factor`` times the usual spacing are dropped."""
    ch = levels.diff(diff) * 100.0
    if isinstance(levels.index, pd.DatetimeIndex) and len(levels) > 2:
        gap = levels.index.to_series().diff(diff).dt.days
        ch = ch[gap <= max_gap_factor * max(gap.median(), 1.0)]
    return ch.dropna(how="any")


def pca_changes(levels: pd.DataFrame, k: int = 3, diff: int = 1, demean: bool = True) -> PCAResult:
    """PCA of yield changes. ``levels``: dates x tenors (yields in %, or in decimals - only
    changes are used, reported in bp if inputs are in %).

    diff: horizon of changes in rows (1 = daily for daily data)."""
    lv = levels
    ch = changes_bp(levels, diff)
    if len(ch) < max(10, ch.shape[1] + 2):
        raise ValueError(f"only {len(ch)} complete changes: too few for PCA")
    X = ch.to_numpy()
    mu = X.mean(axis=0) if demean else np.zeros(X.shape[1])
    C = np.cov(X - mu, rowvar=False)
    evals, evecs = np.linalg.eigh(C)
    order = np.argsort(evals)[::-1]
    evals, evecs = evals[order], evecs[:, order]
    tenors = np.asarray([float(c) for c in lv.columns])
    evecs = _normalise_signs(evecs, tenors)
    scores = pd.DataFrame((X - mu) @ evecs[:, :k], index=ch.index,
                          columns=[f"PC{i + 1}" for i in range(k)])
    return PCAResult(tenors, evecs[:, :k], evals[:k], evals[:k] / evals.sum(), mu, scores,
                     ch.index[0], ch.index[-1], len(ch))


def loading_stability(levels: pd.DataFrame, window: str = "730D", step: str = "365D", k: int = 3):
    """PCA on rolling windows; for each window, the absolute cosine similarity of each
    component's loadings with the full-sample loadings and the variance it explains."""
    full = pca_changes(levels, k)
    lv = levels
    rows = []
    start = lv.index[0]
    end_all = lv.index[-1]
    w, s = pd.Timedelta(window), pd.Timedelta(step)
    while start + w <= end_all + pd.Timedelta("1D"):
        sub = lv[(lv.index >= start) & (lv.index < start + w)]
        if len(changes_bp(sub)) > 60:
            r = pca_changes(sub, k)
            row = {"start": sub.index[0], "end": sub.index[-1], "n": r.n_obs}
            for i in range(k):
                row[f"cos_PC{i + 1}"] = float(abs(r.loadings[:, i] @ full.loadings[:, i]))
                row[f"expl_PC{i + 1}"] = float(r.explained[i])
                row[f"vol_PC{i + 1}"] = float(np.sqrt(r.eigenvalues[i]))
            rows.append(row)
        start = start + s
    return pd.DataFrame(rows)


def decompose_move(levels: pd.DataFrame, d0, d1, pca: PCAResult) -> dict:
    """Split the curve change between two dates into the PCA components plus a residual.

    Returns the observed change per tenor (bp), each component's contribution per tenor,
    the factor scores (in standard deviations of daily moves) and the residual."""
    def row(d):
        return levels.loc[pd.Timestamp(d) if isinstance(levels.index, pd.DatetimeIndex) else d]

    a = row(d0).to_numpy(float)
    b = row(d1).to_numpy(float)
    dy = (b - a) * 100.0
    L = pca.loadings
    f = dy @ L
    contrib = {f"PC{i + 1}": L[:, i] * f[i] for i in range(L.shape[1])}
    resid = dy - sum(contrib.values())
    return {"tenors": pca.tenors, "change": dy, "contrib": contrib, "scores": f,
            "scores_sd": f / np.sqrt(pca.eigenvalues), "residual": resid}


def level_slope_curvature(levels: pd.DataFrame, short: float = 2.0, long: float = 10.0,
                          belly: float | None = None) -> pd.DataFrame:
    """Simple observable factors (in % units of the input): level = mean yield,
    slope = long - short, curvature = 2*belly - short - long."""
    cols = {float(c): c for c in levels.columns}
    b = belly if belly is not None else 5.0
    out = pd.DataFrame(index=levels.index)
    out["level"] = levels.mean(axis=1)
    out["slope"] = levels[cols[long]] - levels[cols[short]]
    if b in cols:
        out["curvature"] = 2 * levels[cols[b]] - levels[cols[short]] - levels[cols[long]]
    return out
