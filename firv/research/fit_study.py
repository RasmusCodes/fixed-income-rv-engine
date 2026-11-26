"""How well do Nelson-Siegel, Svensson and spline curves fit, out of sample, and how
stable are they from one day to the next, across market regimes?

Markets with market-based observations are used: US Treasury par yields, French TEC
yields, Japanese MoF yields (all constant-maturity par yields) and Polish bonds (the
BondSpot fixing, bond by bond). German and UK inputs are themselves central-bank model
curves, so fitting them would only measure one model's ability to copy another.

Three measurements per market and method:

* in-sample RMSE at every month end (bp of the observed yields);
* leave-one-out RMSE at quarter ends: each interior point is dropped, the curve refitted,
  and the dropped yield predicted (interpolation error, the honest fit measure - an
  interpolating cubic spline has zero in-sample error by construction);
* stability: on 60 consecutive observations at the end of each regime, the curves are
  refitted independently every day and the day-to-day change of the fitted yield at
  tenors that are NOT observed is compared with the changes of the observed neighbours
  ("excess noise" ratio > 1 means the model adds movement that is not in the data).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .. import market as M
from ..curves import CurveData, fit, leave_one_out
from .common import REGIMES, regime_of

METHODS = ("ns", "nss", "spline", "cubic")
UNOBSERVED = {"US": (4.0, 8.5, 12.0, 25.0), "FR": (4.0, 6.0, 12.0), "JP": (12.0, 35.0),
              "PL": (6.0, 12.0)}


def _obs(market: str, date) -> CurveData:
    if market == "PL":
        from ..data import poland
        return poland_obs(pd.Timestamp(date))
    return M.observations(market, date)


_PL_CACHE: dict = {}


def poland_obs(date: pd.Timestamp) -> CurveData:
    from ..data import poland
    if "fix" not in _PL_CACHE:
        fix = poland.load_fixings()
        _PL_CACHE["fix"] = fix
        _PL_CACHE["coupons"] = poland.infer_coupons(fix)
    fix = _PL_CACHE["fix"]
    g = fix[fix["date"] == date]
    _, obs, _ = poland.bond_obs_for_date(g, _PL_CACHE["coupons"])
    return CurveData([o.maturity for o in obs], [o.ytm for o in obs], kind="bond", freq=1, bonds=obs)


def _dates(market: str):
    if market == "PL":
        from ..data import poland
        d = pd.DatetimeIndex(sorted(poland.load_fixings()["date"].unique()))
    else:
        d = M.panel(M.MARKETS[market].panel).data.dropna(how="all").index
    return d[d >= pd.Timestamp("1990-01-01")]


def _month_ends(dates: pd.DatetimeIndex) -> pd.DatetimeIndex:
    s = pd.Series(dates, index=dates)
    return pd.DatetimeIndex(s.groupby(pd.Grouper(freq="ME")).last().dropna().values)


def fit_errors(market: str, loo_every: int = 3, log=print) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, loo_rows = [], []
    me = _month_ends(_dates(market))
    for k, d in enumerate(me):
        data = _obs(market, d)
        if (data.kind == "bond" and len(data.bonds) < 6) or (data.kind != "bond" and len(data.tenors) < 6):
            continue
        for m in METHODS:
            try:
                res = fit(m, data)
            except Exception as exc:  # record failure, keep going
                rows.append({"market": market, "date": d, "method": m, "rmse_bp": np.nan, "error": str(exc)[:80]})
                continue
            rows.append({"market": market, "date": d, "regime": regime_of(d), "method": m,
                         "rmse_bp": res.rmse_bp, "max_abs_bp": res.max_abs_bp, "n_obs": len(res.fitted)})
            if k % loo_every == 0:
                loo = leave_one_out(m, data)
                loo = loo[np.isfinite(loo)]
                loo_rows.append({"market": market, "date": d, "regime": regime_of(d), "method": m,
                                 "loo_rmse_bp": float(np.sqrt(np.mean(loo ** 2))) if len(loo) else np.nan,
                                 "loo_max_bp": float(np.max(np.abs(loo))) if len(loo) else np.nan})
        if k % 60 == 0:
            log(f"    {market} fit study {d:%Y-%m} ({k + 1}/{len(me)})")
    return pd.DataFrame(rows), pd.DataFrame(loo_rows)


def stability(market: str, n_obs: int = 60) -> pd.DataFrame:
    """Excess day-to-day noise of fitted yields at unobserved tenors, per regime."""
    dates = _dates(market)
    out = []
    for name, a, b in REGIMES:
        sel = dates[((dates >= pd.Timestamp(a)) if a else True) & ((dates <= pd.Timestamp(b)) if b else True)]
        if len(sel) < n_obs + 1:
            continue
        window = sel[-(n_obs + 1):]
        for m in METHODS:
            fitted, observed = [], []
            taus = []
            for d in window:
                data = _obs(market, d)
                res = fit(m, data)
                freq = 1 if market in ("FR", "PL") else 2
                fitted.append([res.curve.par_yield(T, freq) * 1e4 for T in UNOBSERVED[market]])
                if data.kind == "bond":
                    observed.append(np.array([res.curve.par_yield(T, 1) * 1e4 for T in (5.0, 10.0)]))
                else:
                    observed.append(data.values * 1e4)
                if m in ("ns", "nss"):
                    taus.append(res.curve.params[-2 if m == "nss" else -1])
            F = np.diff(np.asarray(fitted), axis=0)
            row = {"market": market, "regime": name, "method": m, "start": window[0], "end": window[-1]}
            if market != "PL":
                raw = M.panel(M.MARKETS[market].panel).data.loc[window].dropna(axis=1, how="any")
                raw = raw.loc[:, [c for c in raw.columns if float(c) <= M.MARKETS[market].max_tenor]]
                tenors = np.array([float(c) for c in raw.columns])
                O = np.diff(raw.to_numpy(float), axis=0) * 100.0
                ratios = []
                for j, T in enumerate(UNOBSERVED[market]):
                    lo = np.max(np.where(tenors < T)[0]) if np.any(tenors < T) else None
                    hi = np.min(np.where(tenors > T)[0]) if np.any(tenors > T) else None
                    if lo is None or hi is None or O.shape[1] <= hi:
                        continue
                    # noise of the fitted change around the interpolation of neighbours' changes
                    wgt = (T - tenors[lo]) / (tenors[hi] - tenors[lo])
                    interp = (1 - wgt) * O[:, lo] + wgt * O[:, hi]
                    ratios.append(float(np.std(F[:, j] - interp) / max(np.std(interp), 1e-9)))
                    row[f"noise_{T:g}y_bp"] = float(np.std(F[:, j] - interp))
                row["excess_noise_ratio"] = float(np.mean(ratios)) if ratios else np.nan
            else:
                row["fitted_change_sd_bp"] = float(np.mean(np.std(F, axis=0)))
            if taus:
                row["median_abs_dtau"] = float(np.median(np.abs(np.diff(taus))))
            out.append(row)
    return pd.DataFrame(out)


def summarize_fit(errs: pd.DataFrame, loo: pd.DataFrame) -> pd.DataFrame:
    a = errs.groupby(["market", "regime", "method"])["rmse_bp"].median().rename("in_sample_rmse_bp")
    b = loo.groupby(["market", "regime", "method"])["loo_rmse_bp"].median().rename("loo_rmse_bp")
    allr = pd.concat([errs.assign(regime="all"), ]).groupby(["market", "regime", "method"])["rmse_bp"].median()
    allo = loo.assign(regime="all").groupby(["market", "regime", "method"])["loo_rmse_bp"].median()
    t = pd.concat([a, b], axis=1)
    t_all = pd.concat([allr.rename("in_sample_rmse_bp"), allo.rename("loo_rmse_bp")], axis=1)
    return pd.concat([t, t_all]).reset_index()
