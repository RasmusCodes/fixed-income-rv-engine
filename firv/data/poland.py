"""Polish government bond curve from the BondSpot fixing.

Treasury BondSpot Poland publishes a daily fixing for every listed Polish Treasury bond:
bid (K), offer (S) and fixing prices and yields. This module samples the fixing once a
week (Fridays, or the last earlier trading day), keeps fixed-rate lines only (OK zero
coupon, PS 5y, DS 10y, WS 20y; floaters WZ/NZ and inflation-linked IZ are dropped),
infers each bond's coupon from its fixing price and yield (price is linear in the coupon
at a given yield), and fits Nelson-Siegel-Svensson curves to the bonds week by week.

Conventions (checked against the published yields, see tests): annual coupons, ACT/ACT,
maturity and coupon dates on the 25th of the month named in the bond code (PS0527 = 25 May
2027), settlement T+2 business days.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

from ..bonds import Bond, business_days_after, implied_coupon
from .http import PROCESSED, RAW, session

FIXING_URL = "https://www.bondspot.pl/fixing_obligacji"
FOLDER = RAW / "bondspot"
FIXED_TYPES = ("OK", "PS", "DS", "WS")
NAME_RE = re.compile(r"^([A-Z]{2})(\d{2})(\d{2})$")


def parse_name(name: str):
    m = NAME_RE.match(name.strip())
    if not m:
        return None
    kind, mm, yy = m.group(1), int(m.group(2)), int(m.group(3))
    if not 1 <= mm <= 12:
        return None
    return kind, dt.date(2000 + yy, mm, 25)


def _cells(row_html: str):
    cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row_html, re.S)
    return [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in cells]


def _num(x: str):
    x = x.replace(",", ".").replace("\xa0", "").strip()
    try:
        return float(x)
    except ValueError:
        return np.nan


def parse_fixing_page(text: str) -> pd.DataFrame:
    tables = re.findall(r"<table.*?</table>", text, re.S)
    for tb in tables:
        rows = re.findall(r"<tr.*?</tr>", tb, re.S)
        if not rows:
            continue
        head = _cells(rows[0])
        if "ISIN" in head and "Rent fix" in " ".join(head):
            out = []
            for r in rows[1:]:
                c = _cells(r)
                if len(c) < 9:
                    continue
                out.append({"name": c[1], "isin": c[2], "bid_px": _num(c[3]), "ask_px": _num(c[4]),
                            "bid_yld": _num(c[5]), "ask_yld": _num(c[6]), "fix_px": _num(c[7]),
                            "fix_yld": _num(c[8])})
            return pd.DataFrame(out)
    return pd.DataFrame()


def fetch_fixing(day: dt.date, pause: float = 1.0) -> pd.DataFrame | None:
    """Fixing table for one day (cached as CSV). None if the page has no bonds (holiday)."""
    FOLDER.mkdir(parents=True, exist_ok=True)
    target = FOLDER / f"{day:%Y%m%d}.csv"
    empty = FOLDER / f"{day:%Y%m%d}.empty"
    if target.exists():
        return pd.read_csv(target)
    if empty.exists():
        return None
    params = {"date": f"{day:%Y%m%d}", "month": str(day.month), "year": str(day.year)}
    for attempt in range(4):
        try:
            r = session().get(FIXING_URL, params=params, timeout=60)
            if r.status_code == 200:
                break
        except Exception:  # network hiccup
            r = None
        time.sleep(5 * (attempt + 1))
    else:
        raise ConnectionError(f"BondSpot fixing {day} failed")
    time.sleep(pause)
    df = parse_fixing_page(r.text)
    if df.empty:
        empty.write_text("")
        return None
    df.insert(0, "date", day.isoformat())
    df.to_csv(target, index=False)
    return df


def sample_dates(start: dt.date, end: dt.date, weekday: int = 4):
    d = start + dt.timedelta(days=(weekday - start.weekday()) % 7)
    while d <= end:
        yield d
        d += dt.timedelta(days=7)


def collect(start: dt.date = dt.date(2006, 1, 6), end: dt.date | None = None, log=print) -> int:
    """Weekly fixings from ``start`` to ``end`` (resumable; cached per day)."""
    end = end or dt.date.today()
    n, failed = 0, []
    for friday in sample_dates(start, end):
        for back in range(4):
            day = friday - dt.timedelta(days=back)
            if day.weekday() >= 5:
                continue
            try:
                df = fetch_fixing(day)
            except ConnectionError as exc:      # transient: skip, a later run retries it
                failed.append(day)
                log(f"  skipped {day}: {exc}")
                continue
            if df is not None:
                n += 1
                break
        if n and n % 50 == 0:
            log(f"  {n} weekly fixings collected (at {friday})")
    if failed:
        log(f"  {len(failed)} days failed and will be retried on the next run")
    return n


def load_fixings() -> pd.DataFrame:
    files = sorted(FOLDER.glob("*.csv"))
    if not files:
        raise FileNotFoundError("no BondSpot fixings cached; run collect() first")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df["date"] = pd.to_datetime(df["date"])
    parsed = df["name"].map(parse_name)
    df["kind"] = parsed.map(lambda p: p[0] if p else None)
    df["maturity"] = parsed.map(lambda p: pd.Timestamp(p[1]) if p else pd.NaT)
    return df


def infer_coupons(fix: pd.DataFrame, max_obs: int = 25) -> pd.DataFrame:
    """Coupon per ISIN from (fixing price, fixing yield) pairs: median over up to
    ``max_obs`` dates, rounded to 0.25% when that reproduces the published yields."""
    rows = []
    fixed = fix[fix["kind"].isin(FIXED_TYPES) & fix["fix_yld"].notna() & fix["fix_px"].notna()]
    for isin, g in fixed.groupby("isin"):
        g = g.sort_values("date")
        mat = g["maturity"].iloc[0].date()
        kind = g["kind"].iloc[0]
        if kind == "OK":
            rows.append({"isin": isin, "name": g["name"].iloc[0], "kind": kind, "maturity": mat,
                         "coupon": 0.0, "raw": 0.0, "n": len(g), "check_bp": np.nan})
            continue
        pick = g.iloc[np.linspace(0, len(g) - 1, min(max_obs, len(g))).astype(int)]
        est = []
        for _, r in pick.iterrows():
            settle = business_days_after(r["date"].date(), 2)
            if (mat - settle).days < 40:
                continue
            try:
                est.append(implied_coupon(mat, settle, r["fix_px"], r["fix_yld"] / 100.0))
            except (ValueError, ZeroDivisionError):
                pass
        if not est:
            continue
        raw = float(np.median(est))
        rounded = round(raw * 400) / 400.0
        # check: does the rounded coupon reproduce the published yields?
        errs = []
        for _, r in pick.iterrows():
            settle = business_days_after(r["date"].date(), 2)
            if (mat - settle).days < 40:
                continue
            b = Bond(mat, rounded, 1)
            errs.append(abs(b.yield_from_clean(r["fix_px"], settle) * 100 - r["fix_yld"]) * 100)
        check = float(np.median(errs)) if errs else np.nan
        rows.append({"isin": isin, "name": g["name"].iloc[0], "kind": kind, "maturity": mat,
                     "coupon": rounded if (check == check and check < 3.0) else raw, "raw": raw,
                     "n": len(g), "check_bp": check})
    return pd.DataFrame(rows)


def bond_obs_for_date(fix_day: pd.DataFrame, coupons: pd.DataFrame, min_years: float = 0.25):
    """BondObs list (and the bonds' bid-ask in bp) for one fixing date."""
    from ..curves.fitting import BondObs  # noqa: F401  (type used by callers)
    day = fix_day["date"].iloc[0].date()
    settle = business_days_after(day, 2)
    # bonds whose inferred coupon does not reproduce the published yields (two 2006-07 lines)
    # are left out rather than fitted with a wrong cash-flow schedule
    good = coupons[(coupons["kind"] == "OK") | (coupons["check_bp"] < 2.0)]
    cmap = good.set_index("isin")
    obs, info = [], []
    for _, r in fix_day.iterrows():
        if r["isin"] not in cmap.index or not np.isfinite(r["fix_yld"]) or not np.isfinite(r["fix_px"]):
            continue
        c = cmap.loc[r["isin"]]
        mat = c["maturity"] if isinstance(c["maturity"], dt.date) else pd.Timestamp(c["maturity"]).date()
        if (mat - settle).days / 365.25 < min_years:
            continue
        b = Bond(mat, float(c["coupon"]), 1, name=r["name"])
        ytm = r["fix_yld"] / 100.0
        o = b.to_obs(settle, r["fix_px"], ytm)
        obs.append(o)
        info.append({"name": r["name"], "isin": r["isin"], "maturity": mat, "years": o.maturity,
                     "coupon": float(c["coupon"]), "fix_px": r["fix_px"], "fix_yld": r["fix_yld"],
                     "bid_ask_bp": (r["bid_yld"] - r["ask_yld"]) * 100.0})
    return settle, obs, pd.DataFrame(info)


def build_curves(tenors=(1, 2, 3, 4, 5, 7, 10, 15, 20), log=print):
    """Fit NSS to every weekly fixing. Returns (par yields panel %, params, fit stats,
    bond-level residuals for the latest date)."""
    from ..curves.fitting import CurveData, fit_nss
    fix = load_fixings()
    coupons = infer_coupons(fix)
    par_rows, par_idx, prm_rows, stat_rows = [], [], [], []
    last_resid = None
    x0 = None
    for d, g in fix.groupby("date"):
        settle, obs, info = bond_obs_for_date(g, coupons)
        if len(obs) < 6:
            continue
        data = CurveData([o.maturity for o in obs], [o.ytm for o in obs], kind="bond", freq=1, bonds=obs)
        res = fit_nss(data, x0=x0)
        x0 = res.curve.params
        max_t = max(o.maturity for o in obs)
        row = {}
        for T in tenors:
            # at most one year of extrapolation beyond the longest bond (in 2026 the longest
            # fixed-rate line in the fixing, DS0436, has about 9.4 years left)
            row[float(T)] = res.curve.par_yield(float(T), 1) * 100 if T <= max_t + 1.0 else np.nan
        par_rows.append(row)
        par_idx.append(pd.Timestamp(d))
        prm_rows.append(dict(zip(["BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2"], res.curve.params)))
        stat_rows.append({"date": pd.Timestamp(d), "n_bonds": len(obs), "rmse_bp": res.rmse_bp,
                          "max_abs_bp": res.max_abs_bp, "max_maturity": max_t,
                          "median_bid_ask_bp": float(info["bid_ask_bp"].median())})
        info = info.assign(fitted_yld=res.fitted * 100, resid_bp=res.residuals_bp)
        last_resid = info.assign(date=pd.Timestamp(d))
    par = pd.DataFrame(par_rows, index=pd.DatetimeIndex(par_idx, name="date"))
    params = pd.DataFrame(prm_rows, index=par.index)
    stats = pd.DataFrame(stat_rows).set_index("date")
    log(f"  fitted {len(par)} weekly Polish curves; median RMSE {stats['rmse_bp'].median():.2f} bp")
    return par, params, stats, last_resid, coupons


def measured_costs(years: int = 3) -> dict:
    """One-way cost (half the fixing's bid/offer yield spread, bp) by maturity bucket over
    the last ``years`` years: the Polish transaction-cost input to the backtests."""
    fix = load_fixings()
    fix = fix[fix["kind"].isin(FIXED_TYPES) & fix["bid_yld"].notna() & fix["ask_yld"].notna()]
    fix = fix[fix["date"] > fix["date"].max() - pd.DateOffset(years=years)]
    ytm = (fix["maturity"] - fix["date"]).dt.days / 365.25
    half = (fix["bid_yld"] - fix["ask_yld"]) * 100.0 / 2.0
    buckets = {2: (1.5, 3.5), 5: (3.5, 7.0), 10: (7.0, 12.5), 20: (12.5, 30.0)}
    out = {}
    for k, (a, b) in buckets.items():
        sel = half[(ytm >= a) & (ytm < b)]
        if len(sel):
            out[k] = round(float(sel.median()), 2)
    return out


def save_outputs():
    from .loaders import Panel
    par, params, stats, last_resid, coupons = build_curves()
    (PROCESSED / "pl_costs.json").write_text(json.dumps(
        {"one_way_bp_by_tenor": measured_costs(), "method": "median of (bid yield - offer yield)/2 "
         "in the BondSpot fixing over the last 3 years, by residual maturity bucket"}, indent=1))
    Panel("pl_par", par, "par", 1, "bondspot_fixing", "PLN",
          {"derived": "NSS fitted to BondSpot fixing yields, weekly"}).save()
    Panel("pl_params", params, "params", 0, "bondspot_fixing", "PLN").save()
    PROCESSED.mkdir(parents=True, exist_ok=True)
    stats.to_csv(PROCESSED / "pl_fit_stats.csv")
    last_resid.to_csv(PROCESSED / "pl_latest_bonds.csv", index=False)
    coupons.to_csv(PROCESSED / "pl_coupons.csv", index=False)
    return par, stats
