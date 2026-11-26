"""Run the research studies and write tables, charts and generated reports.

    python scripts/run_research.py fit pca strategies scanner country frpl

Outputs go to research/generated/ (markdown tables + CSV) and research/figures/ (PNG).
The written research notes in research/*.md quote these outputs.
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

from firv.research.report import OUT, SERIES, md_table, save, setup_mpl  # noqa: E402

GEN = OUT / "generated"
GEN.mkdir(parents=True, exist_ok=True)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def write(name: str, text: str):
    (GEN / name).write_text(text, encoding="utf-8")
    log(f"wrote research/generated/{name}")


# ------------------------------------------------------------------------------ fit study
def stage_fit(markets=("US", "FR", "JP", "PL")):
    from firv.research import fit_study as FS
    errs, loos, stabs = [], [], []
    for m in markets:
        try:
            e, l = FS.fit_errors(m, log=log)
            s = FS.stability(m)
        except Exception as exc:
            log(f"fit study {m} failed: {exc}")
            continue
        errs.append(e)
        loos.append(l)
        stabs.append(s)
        log(f"fit study {m}: {len(e)} fits, {len(l)} LOO rows")
    errs, loos, stabs = pd.concat(errs), pd.concat(loos), pd.concat(stabs)
    errs.to_csv(GEN / "fit_errors.csv", index=False)
    loos.to_csv(GEN / "fit_loo.csv", index=False)
    stabs.to_csv(GEN / "fit_stability.csv", index=False)
    summ = FS.summarize_fit(errs, loos)
    summ.to_csv(GEN / "fit_summary.csv", index=False)
    piv = summ[summ.regime == "all"].pivot_table(index="market", columns="method",
                                                 values=["in_sample_rmse_bp", "loo_rmse_bp"])
    piv.columns = [f"{a.replace('_rmse_bp', '')} {b}" for a, b in piv.columns]
    reg = summ[summ.regime != "all"].pivot_table(index=["market", "regime"], columns="method",
                                                 values="loo_rmse_bp").reset_index()
    st = stabs.pivot_table(index=["market", "regime"], columns="method",
                           values="excess_noise_ratio").reset_index()
    text = ["# Curve fitting: generated tables", "",
            "Median over month ends (in-sample) and quarter ends (leave-one-out), bp of observed yields.", "",
            md_table(piv.reset_index(), 2), "", "## Leave-one-out RMSE by regime (bp, median)", "",
            md_table(reg, 2), "", "## Stability: excess day-to-day noise at unobserved tenors",
            "", "Ratio of the noise of fitted changes around the interpolated neighbours' changes to the size of those changes (60 consecutive observations at the end of each regime; lower is steadier).", "",
            md_table(st, 3), ""]
    write("01_curve_fitting.md", "\n".join(text))
    chart_fit()


def chart_fit():
    summ = pd.read_csv(GEN / "fit_summary.csv")
    plt = setup_mpl()
    methods = ["ns", "nss", "spline", "cubic"]
    mk = [m for m in ("US", "FR", "JP", "PL") if m in set(summ.market)]
    fig, axes = plt.subplots(1, len(mk), figsize=(3.2 * len(mk), 3.0), sharey=False)
    axes = np.atleast_1d(axes)
    for ax, m in zip(axes, mk):
        s = summ[(summ.market == m) & (summ.regime == "all")].set_index("method")
        x = np.arange(len(methods))
        ax.bar(x - 0.2, [s.loc[k, "in_sample_rmse_bp"] for k in methods], 0.38, label="in sample", color=SERIES[0])
        ax.bar(x + 0.2, [s.loc[k, "loo_rmse_bp"] for k in methods], 0.38, label="leave one out", color=SERIES[1])
        ax.set_xticks(x, ["NS", "NSS", "spline", "cubic"])
        ax.set_title(m)
        ax.set_ylabel("RMSE, bp")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.08))
    save(fig, "fit_rmse_by_method")


STRATEGY_CHART = [("US 2s10s steepener", "static"), ("US 2s10s steepener", "meanrev"),
                  ("US 10y swap spread (long = buy UST, pay fixed)", "meanrev"),
                  ("long FR 10y vs short DE 10y", "meanrev"), ("long PL 10y vs short FR 10y", "meanrev")]


def chart_strategies(series=None):
    """Cumulative net P&L of a few strategies (default parameters, costs x1)."""
    from dataclasses import replace
    from firv.backtest import Spec, run
    from firv.research import strategy_study as SS
    from firv.research.common import build_inputs
    if series is None:
        uni = {name: (legs, kw) for _, name, legs, kw in SS.strategy_universe()}
        series = {}
        for name, sig in STRATEGY_CHART:
            legs, kw = uni[name]
            inp = build_inputs(legs)
            base = Spec(name, legs, **kw)
            if (inp.yields.index.to_series().diff().dt.days.median() or 1) >= 5:
                base = replace(base, lookback=52)
            series[(name, sig)] = run(replace(base, signal=sig), inp)
    plt = setup_mpl()
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for i, (name, sig) in enumerate(STRATEGY_CHART):
        if (name, sig) in series:
            res = series[(name, sig)]
            ax.plot(res.index, res["net"].cumsum(), label=f"{name} [{sig}]", color=SERIES[i % len(SERIES)])
    ax.axhline(0, color="#c3c2b7", lw=0.8)
    ax.set_ylabel("cumulative net P&L, bp per DV01 unit")
    ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    save(fig, "strategy_cumulative")


# ------------------------------------------------------------------------------ PCA
def stage_pca(markets=("US", "DE", "FR", "UK", "JP", "PL")):
    from firv.research import pca_study as PS
    tab, stab, eps, loadings = PS.run(markets)
    tab.to_csv(GEN / "pca_regimes.csv", index=False)
    stab.to_csv(GEN / "pca_rolling.csv", index=False)
    eps.to_csv(GEN / "pca_episodes.csv", index=False)
    (GEN / "pca_loadings.json").write_text(json.dumps(loadings, indent=1))
    roll = stab.groupby("market")[["cos_PC1", "cos_PC2", "cos_PC3", "expl_PC1", "expl_PC2", "expl_PC3"]].agg(["min", "median"])
    roll.columns = [f"{a} {b}" for a, b in roll.columns]
    e = eps.copy()
    e["change_bp"] = e["change_bp"].map(lambda d: ", ".join(f"{k:g}y {v:+.0f}" for k, v in d.items()))
    text = ["# PCA of curve changes: generated tables", "",
            "Daily changes of par yields (weekly for Poland), 2000 onward.", "",
            md_table(tab, 3), "", "## Rolling 2-year windows vs full sample (cosine of loadings, share explained)",
            "", md_table(roll.reset_index(), 3), "", "## Largest 63-observation moves in level (PC1) and slope (PC2)",
            "", md_table(e[["market", "factor", "start", "end", "pc_scores_bp", "residual_rms_bp", "change_bp"]], 1), ""]
    write("02_pca.md", "\n".join(text))
    plt = setup_mpl()
    mk = list(loadings)
    fig, axes = plt.subplots(2, 3, figsize=(10, 5.6), sharey=True)
    for ax, m in zip(axes.ravel(), mk):
        L = np.array(loadings[m]["loadings"])
        t = loadings[m]["tenors"]
        for k in range(3):
            ax.plot(t, L[:, k], marker="o", ms=3, label=f"PC{k + 1} ({loadings[m]['explained'][k] * 100:.0f}%)",
                    color=SERIES[k])
        ax.axhline(0, color="#c3c2b7", lw=0.8)
        ax.set_title(m)
        ax.set_xscale("log")
        ax.set_xticks([1, 2, 5, 10, 30], ["1", "2", "5", "10", "30"])
        ax.legend(fontsize=7, loc="lower right")
    fig.supxlabel("tenor, years (log scale)")
    fig.supylabel("loading")
    save(fig, "pca_loadings")


# ------------------------------------------------------------------------------ strategies
def stage_strategies(markets=("US", "DE", "FR", "UK", "JP", "PL")):
    from firv.research import strategy_study as SS
    from firv.backtest import performance
    keep = {("US 10y swap spread (long = buy UST, pay fixed)", "meanrev"),
            ("US 2s10s steepener", "static"), ("US 2s10s steepener", "meanrev"),
            ("long FR 10y vs short DE 10y", "meanrev"), ("long PL 10y vs short FR 10y", "meanrev")}
    tab, ser = SS.run_all(markets, log=log, keep_series=keep)
    xc = SS.cross_country_carry()
    p = performance(xc)
    tab = pd.concat([tab, pd.DataFrame([{"family": "carry", "strategy": "cross-country 10y carry/vol (long best, short worst)",
                                         "signal": "carry", "test": "full sample, costs x1", **p}])], ignore_index=True)
    tab.to_csv(GEN / "strategies.csv", index=False)
    cols = ["family", "strategy", "signal", "test", "start", "end", "ann_return_bp", "ann_vol_bp", "sharpe",
            "t_nw", "max_dd_bp", "cost_bp_per_year", "turnover_per_year"]
    main = tab[tab.test == "full sample, costs x1"]
    oos = tab[tab.test.isin(["out-of-sample (second half)", "walk-forward OOS", "in-sample (first half, chosen params)"])]
    text = ["# Strategy backtests: generated tables", "",
            "P&L in bp per unit of DV01 per year (1 unit = the trade's DV01 per bp). Costs at 1x the assumptions unless stated.", "",
            "## Full sample, fixed default parameters", "", md_table(main[cols], 2), "",
            "## Mean reversion: in-sample choice, out-of-sample and walk-forward", "",
            md_table(oos[cols + ["params"]], 2), "",
            "## Cost sensitivity (full sample)", "",
            md_table(tab[tab.test.str.startswith("full sample")].pivot_table(
                index=["strategy", "signal"], columns="test", values="sharpe").reset_index(), 2), ""]
    write("03_strategies.md", "\n".join(text))
    chart_strategies(ser)


# ------------------------------------------------------------------------------ scanner
def stage_scanner(markets=("US", "DE", "FR", "UK", "JP", "PL")):
    from firv import scanner
    table, resid = scanner.scan(markets)
    table.to_csv(GEN / "scanner.csv", index=False)
    resid.to_csv(GEN / "scanner_pca_residuals.csv", index=False)
    cols = ["market", "trade", "asof", "level_bp", "z_1y", "z_3y", "pct_5y", "chg_3m_bp", "carry_roll_3m",
            "vol_ann_bp", "carry_to_vol", "half_life_w", "mr_side"]
    text = ["# Relative-value scanner: generated snapshot", "",
            "Sorted by |z_1y|. X is the spread each trade gains from; see firv/scanner.py for definitions.", "",
            md_table(table[cols], 2), "", "## PCA rich/cheap by tenor (3 factors on 2 years of levels)", "",
            md_table(resid, 2), ""]
    write("04_scanner.md", "\n".join(text))


# ------------------------------------------------------------------------------ country
def stage_country(markets=("US", "DE", "FR", "UK", "JP", "PL")):
    from firv.research import country as C
    snap = C.snapshot(markets)
    snap.to_csv(GEN / "country_snapshot.csv", index=False)
    sh = C.spread_history()
    sh.to_csv(GEN / "spread_history_10y.csv")
    t = snap.set_index("market").T.reset_index().rename(columns={"index": "measure"})
    write("05_country_comparison.md", "\n".join(["# Country comparison: generated snapshot", "",
                                                 md_table(t, 2), ""]))
    plt = setup_mpl()
    fig, ax = plt.subplots(figsize=(8, 3.4))
    for i, c in enumerate(sh.columns):
        ax.plot(sh.index, sh[c], label=c, color=SERIES[i])
    ax.axhline(0, color="#c3c2b7", lw=0.8)
    ax.set_ylabel("10y spread, bp")
    ax.legend(fontsize=7, ncol=5, loc="upper left")
    save(fig, "spreads_10y")


# ------------------------------------------------------------------------------ France vs Poland
def stage_frpl():
    from firv.research import france_poland as FP
    out = FP.run_case()
    for k in ("spreads", "co_movement", "hedge", "trades", "macro"):
        out[k].to_csv(GEN / f"frpl_{k}.csv")
    sp, cm, hc, tr = out["spreads"], out["co_movement"], out["hedge"], out["trades"]
    last = out["panel"].index[-1]
    lv = pd.DataFrame({"measure": list(sp.columns), "now_bp": sp.iloc[-1].values,
                       "1y_ago_bp": sp.loc[:last - pd.DateOffset(years=1)].iloc[-1].values,
                       "5y_mean_bp": sp.loc[last - pd.DateOffset(years=5):].mean().values,
                       "5y_min_bp": sp.loc[last - pd.DateOffset(years=5):].min().values,
                       "5y_max_bp": sp.loc[last - pd.DateOffset(years=5):].max().values})
    cols = ["trade", "signal", "test", "start", "end", "ann_return_bp", "ann_vol_bp", "sharpe", "t_nw",
            "max_dd_bp", "cost_bp_per_year", "params"]
    text = ["# France vs Poland: generated tables", "", f"Weekly data to {last:%Y-%m-%d}.", "",
            md_table(lv, 1), "", "## Co-movement (52-week windows, latest)", "",
            md_table(cm.dropna().tail(1).reset_index(), 3), "",
            "## FX-hedged comparison (PLN hedged into EUR via short-rate differential)", "",
            md_table(hc.dropna().tail(1).reset_index(), 3), "",
            "## Candidate trades", "", md_table(tr[[c for c in cols if c in tr.columns]], 2), "",
            "## Macro and fiscal (OECD; policy rates from BIS)", "", md_table(out["macro"], 2), ""]
    write("06_france_vs_poland.md", "\n".join(text))
    plt = setup_mpl()
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    for i, c in enumerate(["PL-FR 2y", "PL-FR 5y", "PL-FR 10y"]):
        axes[0].plot(sp.index, sp[c], label=c, color=SERIES[i])
    axes[0].axhline(0, color="#c3c2b7", lw=0.8)
    axes[0].set_title("Poland minus France, local-currency yields")
    axes[0].set_ylabel("bp")
    axes[0].legend(fontsize=7)
    axes[1].plot(hc.index, hc["hedged_pickup_bp"], color=SERIES[0], label="PL 10y hedged to EUR minus FR 10y")
    axes[1].plot(sp.index, sp["PL-FR 10y"], color=SERIES[1], label="unhedged PL-FR 10y")
    axes[1].axhline(0, color="#c3c2b7", lw=0.8)
    axes[1].set_title("10y pickup: hedged vs unhedged")
    axes[1].set_ylabel("bp")
    axes[1].legend(fontsize=7)
    save(fig, "frpl_spreads")
    fig, ax = plt.subplots(figsize=(8, 3.0))
    ax.plot(cm.index, cm["beta_PL_on_FR"], label="beta of PL 10y on FR 10y (52w)", color=SERIES[0])
    ax.plot(cm.index, cm["corr"], label="correlation (52w)", color=SERIES[1])
    ax.axhline(0, color="#c3c2b7", lw=0.8)
    ax.legend(fontsize=7)
    save(fig, "frpl_beta")


STAGES = {"fit": stage_fit, "pca": stage_pca, "strategies": stage_strategies,
          "scanner": stage_scanner, "country": stage_country, "frpl": stage_frpl,
          "charts": lambda: (chart_fit(), chart_strategies())}

if __name__ == "__main__":
    for s in sys.argv[1:] or list(STAGES):
        t0 = time.time()
        log(f"stage {s} ...")
        STAGES[s]()
        log(f"stage {s} done in {time.time() - t0:.0f}s")
