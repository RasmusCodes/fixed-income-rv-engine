"""Export compact JSON for the interactive terminal (web/data/*.json).

Per market: weekly observations since 2000 (the inputs the browser fits curves to), the
weekly funding rate, PCA loadings, the largest historical moves (scenarios) and source
metadata. Shared: scanner snapshot, country comparison, France-vs-Poland series.

Not exported: raw BondSpot fixings (Poland is exported as fitted par yields), ICE swap
rates and Moody's yields (vendor data via FRED).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from firv import market as M  # noqa: E402
from firv.data.loaders import Panel  # noqa: E402
from firv.data.sources import SOURCES  # noqa: E402

OUT = ROOT / "web" / "data"
GEN = ROOT / "research" / "generated"
START = "2000-01-01"

OBS = {
    # market: (panel, kind, tenors to export or None = all published up to max)
    "US": ("us_par", "par", None),
    "DE": ("de_zero", "zero", [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30]),
    "FR": ("fr_tec", "par", None),
    "UK": ("uk_nominal", "zero", [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40]),
    "JP": ("jp_par", "par", None),
    "PL": ("pl_par", "par", None),
}
CLASS_NOTE = {
    "US": "Official: U.S. Treasury par yield curve (constant maturity, semiannual).",
    "DE": "Official estimate: Bundesbank zero-coupon curve (Svensson method, continuous compounding).",
    "FR": "Official: Banque de France TEC constant-maturity OAT yields (index computed by Euronext).",
    "UK": "Official estimate: Bank of England nominal government liability curve (spline, continuous compounding).",
    "JP": "Official: Ministry of Finance JGB constant-maturity yields.",
    "PL": "Derived in this project: weekly Nelson-Siegel-Svensson fit to the BondSpot fixing of Polish government bonds; par yields shown, raw fixings not redistributed.",
}
FUNDING_LABEL = {"US": "SOFR (3m bill before 2018)", "DE": "EUR STR (6m Bund before Oct 2019)",
                 "FR": "EUR STR (6m Bund before Oct 2019)", "UK": "Bank Rate", "JP": "BoJ policy rate",
                 "PL": "NBP reference rate"}


def clean(v, nd=3):
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return None
    if isinstance(v, (np.floating, float)):
        return round(float(v), nd)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (pd.Timestamp,)):
        return v.strftime("%Y-%m-%d")
    return v


def weekly(df: pd.DataFrame) -> pd.DataFrame:
    w = df.resample("W-FRI").last().dropna(how="all")
    return w[w.index >= pd.Timestamp(START)]


def export_market(m: str, pca: dict, episodes: pd.DataFrame):
    name, kind, tenors = OBS[m]
    mk = M.MARKETS[m]
    df = Panel.load(name).data
    cols = [float(c) for c in df.columns]
    if tenors is None:
        keep = [c for c in df.columns if float(c) <= mk.max_tenor + 1e-9]
    else:
        keep = [df.columns[int(np.argmin([abs(c - t) for c in cols]))] for t in tenors]
    df = df[keep]
    df = df.loc[:, df.notna().sum() > 20]
    w = weekly(df)
    # last available daily observation as the final row (it may be mid-week)
    last_day = df.dropna(how="all").index[-1]
    if last_day not in w.index:
        w = w[w.index < last_day]
        w.loc[last_day] = df.loc[last_day]
    w.index = [d if d != last_day else last_day for d in w.index]
    fund = M.funding_rate(m).reindex(pd.DatetimeIndex(w.index), method="ffill")
    t = [float(c) for c in w.columns]
    out = {
        "code": m, "name": mk.name, "currency": mk.currency, "kind": kind, "freq": mk.freq,
        "classification": CLASS_NOTE[m], "source": SOURCES[mk.source], "funding_label": FUNDING_LABEL[m],
        "tenors": t, "dates": [d.strftime("%Y-%m-%d") for d in w.index],
        "values": [[clean(v) for v in row] for row in w.to_numpy(float)],
        "funding": [clean(v) for v in fund.to_numpy(float)],
        "pca": pca.get(m), "max_tenor": mk.max_tenor,
        "episodes": [],
    }
    if episodes is not None and len(episodes):
        for _, e in episodes[episodes.market == m].iterrows():
            ch = e["change_bp"]
            if isinstance(ch, str):
                import ast
                ch = ast.literal_eval(ch.replace("np.float64(", "").replace(")", ""))
            out["episodes"].append({"factor": e["factor"], "start": str(e["start"])[:10], "end": str(e["end"])[:10],
                                    "change_bp": {str(k): clean(v, 1) for k, v in ch.items()}})
    if m == "PL":
        st = pd.read_csv(ROOT / "data" / "processed" / "pl_fit_stats.csv", parse_dates=["date"]).set_index("date")
        out["fit_stats"] = {"median_rmse_bp": clean(st["rmse_bp"].median(), 2),
                            "latest_rmse_bp": clean(st["rmse_bp"].iloc[-1], 2),
                            "latest_n_bonds": int(st["n_bonds"].iloc[-1]),
                            "latest_max_maturity": clean(st["max_maturity"].iloc[-1], 2)}
    path = OUT / f"{m}.json"
    path.write_text(json.dumps(out, separators=(",", ":")))
    return path, len(w), len(t)


def export_common():
    out = {"generated": pd.Timestamp.today().strftime("%Y-%m-%d")}
    sc = pd.read_csv(GEN / "scanner.csv")
    cols = ["market", "family", "trade", "asof", "level_bp", "z_1y", "z_3y", "pct_5y", "chg_3m_bp",
            "carry_roll_3m", "vol_ann_bp", "carry_to_vol", "half_life_w"]
    out["scanner"] = [{c: clean(r[c], 2) for c in cols} for _, r in sc.iterrows()]
    rs = pd.read_csv(GEN / "scanner_pca_residuals.csv")
    out["pca_residuals"] = [{c: clean(r[c], 2) for c in rs.columns} for _, r in rs.iterrows()]
    cs = pd.read_csv(GEN / "country_snapshot.csv")
    out["country"] = [{c: clean(r[c], 3) for c in cs.columns} for _, r in cs.iterrows()]
    sp = pd.read_csv(GEN / "frpl_spreads.csv", index_col=0, parse_dates=True)
    hc = pd.read_csv(GEN / "frpl_hedge.csv", index_col=0, parse_dates=True)
    cm = pd.read_csv(GEN / "frpl_co_movement.csv", index_col=0, parse_dates=True)
    fr = pd.DataFrame({"pl_fr_2y": sp["PL-FR 2y"], "pl_fr_5y": sp["PL-FR 5y"], "pl_fr_10y": sp["PL-FR 10y"],
                       "slope_gap": sp["slope gap (PL-FR 2s10s)"], "hedged_pickup": hc["hedged_pickup_bp"],
                       "beta": cm["beta_PL_on_FR"], "corr": cm["corr"]}).dropna(subset=["pl_fr_10y"])
    out["frpl"] = {"dates": [d.strftime("%Y-%m-%d") for d in fr.index],
                   **{c: [clean(v, 2) for v in fr[c].to_numpy(float)] for c in fr.columns}}
    tr = pd.read_csv(GEN / "frpl_trades.csv", index_col=0)
    keep = ["trade", "signal", "test", "start", "end", "ann_return_bp", "ann_vol_bp", "sharpe", "t_nw", "max_dd_bp",
            "cost_bp_per_year"]
    out["frpl_trades"] = [{c: clean(r.get(c), 2) for c in keep} for _, r in tr.iterrows()]
    fx = weekly(Panel.load("fx_eur").data[["PLN", "USD", "GBP", "JPY"]].ffill())
    out["fx"] = {"note": "ECB euro reference rates, units per EUR, last observation of each week",
                 "dates": [d.strftime("%Y-%m-%d") for d in fx.index],
                 **{c: [clean(v, 5) for v in fx[c].to_numpy(float)] for c in fx.columns}}
    out["sources"] = SOURCES
    (OUT / "common.json").write_text(json.dumps(out, separators=(",", ":"), default=str))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pca = json.loads((GEN / "pca_loadings.json").read_text()) if (GEN / "pca_loadings.json").exists() else {}
    eps = pd.read_csv(GEN / "pca_episodes.csv") if (GEN / "pca_episodes.csv").exists() else None
    for m in OBS:
        p, n, k = export_market(m, pca, eps)
        print(f"{m}: {n} weeks x {k} tenors -> {p.name} ({p.stat().st_size / 1024:.0f} KB)")
    export_common()
    print(f"common.json ({(OUT / 'common.json').stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
