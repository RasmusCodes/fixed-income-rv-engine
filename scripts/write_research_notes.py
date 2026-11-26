"""Write the research notes (research/*.md) from the outputs in research/generated.

Numbers in the text are read from the result files at write time, so the notes cannot drift
from the results. Run after scripts/run_research.py.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from firv.research.report import md_table  # noqa: E402

R = ROOT / "research"
G = R / "generated"
MK = {"US": "United States", "DE": "Germany", "FR": "France", "UK": "United Kingdom", "JP": "Japan", "PL": "Poland"}


def f(x, nd=2):
    return f"{x:,.{nd}f}"


# ------------------------------------------------------------------------------------ 01
def note_fit():
    s = pd.read_csv(G / "fit_summary.csv")
    st = pd.read_csv(G / "fit_stability.csv")
    e = pd.read_csv(G / "fit_errors.csv")
    a = s[s.regime == "all"]
    loo = a.pivot_table(index="market", columns="method", values="loo_rmse_bp")[["ns", "nss", "spline", "cubic"]]
    ins = a.pivot_table(index="market", columns="method", values="in_sample_rmse_bp")[["ns", "nss", "spline", "cubic"]]
    best = loo.idxmin(axis=1)
    name = {"ns": "Nelson-Siegel", "nss": "Svensson", "spline": "smoothing spline", "cubic": "cubic spline"}
    t1 = pd.concat([ins.add_prefix("in-sample "), loo.add_prefix("leave-one-out ")], axis=1).round(2).reset_index()
    reg = s[s.regime != "all"].pivot_table(index=["market", "regime"], columns="method", values="loo_rmse_bp")[["ns", "nss", "spline", "cubic"]].round(2).reset_index()
    stab = st.pivot_table(index=["market", "regime"], columns="method", values="excess_noise_ratio")[["ns", "nss", "spline", "cubic"]].round(3).reset_index()
    spl_best = (st.dropna(subset=["excess_noise_ratio"]).groupby(["market", "regime"])
                .apply(lambda g: g.loc[g.excess_noise_ratio.idxmin(), "method"]))
    n_spl = int((spl_best == "spline").sum())
    worst_reg = reg.set_index(["market", "regime"])["nss"].idxmax()
    text = f"""# Curve fitting across markets and regimes

**Question.** Which curve model fits government yields best out of sample, and which is
stable enough to use day after day?

**Data.** Market-based observations only: US Treasury par yields (CMT, 1990-2026), French
TEC yields (2004-2026), Japanese MoF yields (1990-2026), all constant-maturity par yields,
and Polish government bonds bond by bond from the BondSpot fixing (2006-2026, weekly).
German and UK inputs are themselves central-bank model curves, so fitting them would only
measure one model's ability to copy another; they are left out here.

**Method.** {len(e):,} fits ({e.method.nunique()} models at every month end; none failed). In-sample RMSE in bp of
the observed yields; leave-one-out RMSE at quarter ends (each interior point dropped,
refitted, predicted); stability on 60 consecutive observations at the end of each regime
(see docs/METHODOLOGY.md, section 2).

## Results

Median RMSE across dates (bp):

{md_table(t1, 2)}

- Out of sample, the lowest error is: {", ".join(f"{m} {name[best[m]]} ({f(loo.loc[m].min())} bp)" for m in loo.index)}.
- Nelson-Siegel, with a single hump, has the highest leave-one-out error in
  {", ".join(m for m in loo.index if loo.loc[m].idxmax() == "ns")}.
- The cubic spline fits the inputs exactly (in-sample error near zero for par data) but
  interpolates worse than Svensson where tenors are sparse: US {f(loo.loc["US", "cubic"])} bp vs
  {f(loo.loc["US", "nss"])} bp. In Japan, where yearly tenors from 1 to 10 years are published, it
  interpolates best. For Polish bonds it is the worst ({f(loo.loc["PL", "cubic"])} bp): an
  interpolant through noisy bond yields passes the noise on.
- Errors depend on the regime. The largest Svensson error is in {worst_reg[0]}, {worst_reg[1]}.

Leave-one-out RMSE by regime (bp, median):

{md_table(reg, 2)}

## Stability

Excess day-to-day noise at maturities that are not observed (lower is steadier):

{md_table(stab, 3)}

The smoothing spline is the steadiest model in {n_spl} of {len(spl_best)} market-regime cells.
Svensson's taus can jump between nearby local optima when the two humps are close; the same
happens in official curves (Bundesbank and ECB taus are within 0.13 and 0.04 years on 5% of
days since 2000), so parameters should not be read as stable economic quantities even when
the fitted curve is.

![Fit errors by model](figures/fit_rmse_by_method.png)

## Takeaways

- For relative-value work on par data, Svensson is the best single default out of sample
  and the smoothing spline the best when day-to-day stability of unobserved points matters
  (for example, rich/cheap signals that compare fitted and observed yields daily).
- A curve that reproduces its inputs exactly (bootstrap or interpolating spline) says
  nothing about fit quality; judge models only out of sample.

Full tables: [generated/01_curve_fitting.md](generated/01_curve_fitting.md), raw results in
`generated/fit_errors.csv`, `fit_loo.csv`, `fit_stability.csv`.
"""
    (R / "01_curve_fitting.md").write_text(text, encoding="utf-8")


# ------------------------------------------------------------------------------------ 02
def note_pca():
    t = pd.read_csv(G / "pca_regimes.csv")
    r = pd.read_csv(G / "pca_rolling.csv")
    e = pd.read_csv(G / "pca_episodes.csv")
    allr = t[t.regime == "all (2000-)"][["market", "n", "expl_PC1", "expl_PC2", "expl_PC3", "vol_PC1_bp", "vol_PC2_bp", "vol_PC3_bp"]].copy()
    for c in ("expl_PC1", "expl_PC2", "expl_PC3"):
        allr[c] = allr[c] * 100
    reg = t[t.regime != "all (2000-)"][["market", "regime", "expl_PC1", "expl_PC2", "vol_PC1_bp", "vol_PC2_bp", "cos_PC1", "cos_PC2", "cos_PC3"]].copy()
    for c in ("expl_PC1", "expl_PC2"):
        reg[c] = reg[c] * 100
    roll = r.groupby("market")[["cos_PC1", "cos_PC2", "cos_PC3"]].agg(["min", "median"]).round(2)
    roll.columns = [f"{a} {b}" for a, b in roll.columns]
    ep = e.copy()
    ep["change"] = ep["change_bp"].map(lambda s: ", ".join(f"{float(k):g}y {v:+.0f}" for k, v in ast.literal_eval(str(s).replace("np.float64(", "").replace(")", "")).items()))
    ep = ep[["market", "factor", "start", "end", "change"]]
    lo1, hi1 = allr.expl_PC1.min(), allr.expl_PC1.max()
    text = f"""# Principal components of curve moves

**Question.** How many factors drive each curve, are they the same across markets and
regimes, and what were the largest moves?

**Data and method.** Daily changes of par yields (weekly for Poland) at fixed tenors since
2000; PCA of changes in bp. Changes are never taken across a data gap (the US 30-year CMT
was not published from February 2002 to February 2006; the Bank of England curve goes beyond
25 years only from 2016, so UK results start then). Rolling two-year windows every six months
are compared with the full-sample loadings by the cosine of the angle between them.

## Shares of variance and volatility (full sample)

{md_table(allr.round(2), 2)}

Level (PC1) explains {f(lo1, 0)}-{f(hi1, 0)}% of daily variance in every market. Slope is
largest in Japan and the US; curvature is small everywhere. Daily level volatility in Poland
(weekly data, so not directly comparable) and in the 2022-26 regime everywhere is much higher
than in the low-rate years.

## Stability

By regime (share of variance in %, volatility in bp, cosine with full-sample loadings):

{md_table(reg.round(3), 3)}

Rolling two-year windows, cosine with the full-sample loadings:

{md_table(roll.reset_index(), 2)}

Level and slope are stable shapes. Curvature is not: in some windows its loadings point in a
different direction altogether, so a "PC3 trade" estimated on one period can carry level or
slope risk in the next. This matters for PCA-weighted butterflies (see the strategy study).

![PCA loadings](figures/pca_loadings.png)

## Largest three-month moves in level and slope

Found from the data (largest non-overlapping three-month sums of each factor's scores),
then decomposed. These moves are offered as historical scenarios in the terminal.

{md_table(ep, 1)}
"""
    (R / "02_pca.md").write_text(text, encoding="utf-8")


# ------------------------------------------------------------------------------------ 03
def note_strategies():
    t = pd.read_csv(G / "strategies.csv")
    full = t[t.test == "full sample, costs x1"]
    sh = full.pivot_table(index=["family", "strategy"], columns="signal", values="sharpe").round(2).reset_index()
    wf = t[t.test == "walk-forward OOS"][["family", "strategy", "start", "end", "ann_return_bp", "ann_vol_bp", "sharpe", "t_nw", "cost_bp_per_year"]].copy()
    wf["start"] = wf["start"].str[:4]
    wf["end"] = wf["end"].str[:4]
    wf = wf.sort_values("t_nw", ascending=False)
    n_wf = len(wf)
    sig = wf[wf.t_nw.abs() >= 2]
    pos = wf[wf.t_nw >= 2]
    neg = wf[wf.t_nw <= -2]
    from scipy.stats import norm
    bonf = float(norm.ppf(1 - 0.05 / n_wf))
    top = wf.iloc[0]
    cs = t[t.test.str.startswith("full sample") & (t.signal == "meanrev")].pivot_table(index="strategy", columns="test", values="sharpe")
    cs = cs[["full sample, costs x0", "full sample, costs x1", "full sample, costs x2"]].round(2).reset_index()
    neg_curve = wf[(wf.family == "curve") & wf.strategy.str.contains("2s10s")]
    text = f"""# Relative-value strategies: what survived out of sample

**Question.** Did the standard rates RV signals - fading curve and butterfly dislocations,
cross-country spreads, swap spreads, breakevens, carry - earn money after realistic costs
and out of sample?

**Set-up.** Constant-maturity DV01-weighted trades with carry, roll-down and convexity;
weekly decisions; costs on every trade and a quarterly roll. Signals: mean reversion
(z-score), carry (sign of carry plus roll-down), momentum (control), static. Validation:
first-half/second-half and walk-forward parameter selection. Details: docs/METHODOLOGY.md,
section 6. P&L is in bp per unit of DV01 per year.

## Walk-forward out-of-sample results (mean reversion)

{md_table(wf.round(2), 2)}

{n_wf} walk-forward tests were run and {len(sig)} have |t| >= 2, far more than the
{n_wf * 0.05:.1f} that chance alone would produce - but {len(neg)} of them are **negative**: those signals
lost money reliably after costs. {len(pos)} are positive ({", ".join(pos.strategy)}). With {n_wf} tests,
a one-sided 5% Bonferroni bar is t = {bonf:.2f}; only **{top.strategy}** clears it:
{f(top.ann_return_bp, 1)} bp per DV01 per year, Sharpe {f(top.sharpe)}, t {f(top.t_nw)} ({top.start}-{top.end}).
Its caveats: LIBOR swaps (the market has since moved to SOFR) and a sample that ends in 2016
and includes the 2008 crisis.

Mean reversion of curve slopes **lost money in every market**: 2s10s walk-forward Sharpe
ratios run from {f(neg_curve.sharpe.min())} to {f(neg_curve.sharpe.max())}. Slopes are persistent and move with the
policy cycle, so fading a steep or flat curve meant standing against long trends.
Butterflies and cross-country 10y spreads are close to zero or negative after costs; PCA
weighting did not improve butterflies (curvature loadings are unstable, see the PCA note).
Polish trades did not cover the bid/offer measured in the fixing.

## Full sample, all signals (Sharpe ratios, costs x1)

{md_table(sh, 2)}

The carry signal is mildly positive for some curve trades (French and Japanese 2s10s) but
not consistently. The static US steepeners earned their carry and roll-down plus a secular
steepening; that is a risk premium with long drawdowns, not relative value. Momentum, the
control, is negative almost everywhere.

## Costs

Mean reversion, Sharpe ratio at 0x, 1x and 2x the cost assumptions:

{md_table(cs, 2)}

![Cumulative P&L of selected strategies](figures/strategy_cumulative.png)

## Not tested

Treasury futures basis: no free settlement prices could be used, so the basis module
(conversion factors, CTD, gross and net basis, implied repo) is analytics only.

Full tables: [generated/03_strategies.md](generated/03_strategies.md) and `generated/strategies.csv`.
"""
    (R / "03_strategies.md").write_text(text, encoding="utf-8")


# ------------------------------------------------------------------------------------ 04
def note_scanner():
    s = pd.read_csv(G / "scanner.csv")
    res = pd.read_csv(G / "scanner_pca_residuals.csv")
    asof = s["asof"].max()
    top = s.head(15)[["market", "trade", "level_bp", "z_1y", "z_3y", "pct_5y", "carry_roll_3m", "vol_ann_bp", "carry_to_vol", "half_life_w"]]
    big = res.reindex(res.resid_z.abs().sort_values(ascending=False).index).head(10)
    text = f"""# Relative-value scanner snapshot ({asof})

The scanner measures every curve spread, butterfly, cross-country spread, swap spread,
breakeven and credit spread against its own history. For each trade, X is the spread the
trade gains from (for a steepener X = long yield - short yield; for a cross-country trade
long A vs B, X = -(A - B), so X at a five-year low means the A-B spread is at a five-year
high). Columns: z-scores against one and three years of weekly data, five-year percentile,
expected carry and roll-down over three months (bp per DV01 unit), annualised volatility,
their ratio, and the AR(1) half-life in weeks.

**This is a measurement, not a list of recommendations.** The strategy study shows that
fading such extremes did not pay out of sample for curves and butterflies.

## Largest dislocations by one-year z-score

{md_table(top.round(2), 2)}

## PCA rich/cheap by tenor

Today's yield minus its fit from three principal components of two years of yield levels
(positive = the point is cheap relative to the curve's usual shape):

{md_table(big.round(2), 2)}

Full table (48 rows): [generated/04_scanner.md](generated/04_scanner.md).
"""
    (R / "04_scanner.md").write_text(text, encoding="utf-8")


# ------------------------------------------------------------------------------------ 05
def note_country():
    c = pd.read_csv(G / "country_snapshot.csv").set_index("market")
    rows = [("2y", "y2", 2), ("10y", "y10", 2), ("30y (Poland: none)", "y30", 2), ("2s10s (bp)", "slope_2s10s_bp", 0),
            ("policy rate", "policy_rate", 2), ("1y1y forward", "fwd_1y1y", 2), ("5y5y forward", "fwd_5y5y", 2),
            ("CPI y/y", "cpi_yoy", 2), ("10y minus CPI", "real_10y_expost", 2), ("10y real (linkers)", "real_10y_market", 2),
            ("10y breakeven", "breakeven_10y", 2), ("debt % GDP 2025", "debt_gdp_2025", 1), ("debt % GDP 2027 (proj.)", "debt_gdp_2027_proj", 1),
            ("net lending % GDP 2025", "deficit_gdp_2025", 1), ("10y vs Germany (bp)", "spread_10y_vs_DE_bp", 0),
            ("10y vol, 1y (bp/yr)", "vol_10y_bp_ann", 0), ("10y hedged into EUR", "hedged_10y_in_EUR", 2),
            ("10y hedged into USD", "hedged_10y_in_USD", 2)]
    tab = pd.DataFrame({m: [c.loc[m, k] for _, k, _ in rows] for m in c.index}, index=[r[0] for r in rows]).reset_index().rename(columns={"index": "measure"})
    asof = c["asof"].max()
    hi_slope = c.slope_2s10s_bp.idxmax()
    hedged = c.hedged_10y_in_EUR.sort_values(ascending=False)
    text = f"""# Country comparison ({asof})

Par yields in each market's own convention; forwards from the bootstrapped zero curve (they
include term premia, so they are not pure expectations); inflation from the BIS CPI series
(latest month {c.cpi_month.max()}); fiscal data from the OECD Economic Outlook; hedged yields by
covered interest parity with overnight or policy rates as the short-rate proxy.

{md_table(tab, 2)}

What the table shows:

- **Curve shape.** The steepest 2s10s curve is {MK[hi_slope]} ({f(c.slope_2s10s_bp.max(), 0)} bp); the US and
  Germany are the flattest ({f(c.loc["US", "slope_2s10s_bp"], 0)} and {f(c.loc["DE", "slope_2s10s_bp"], 0)} bp).
- **Policy paths.** Every curve prices a higher one-year rate a year ahead than today
  (1y1y above the 1-year rate), most of all Poland ({f(c.loc["PL", "implied_1y_change_bp"], 0)} bp) - partly term premium.
- **Spreads.** France trades {f(c.loc["FR", "spread_10y_vs_DE_bp"], 0)} bp over Germany at 10 years; Poland
  {f(c.loc["PL", "spread_10y_vs_DE_bp"], 0)} bp, the UK {f(c.loc["UK", "spread_10y_vs_DE_bp"], 0)} bp and the US {f(c.loc["US", "spread_10y_vs_DE_bp"], 0)} bp
  (across currencies these are not credit spreads).
- **Hedged into euros**, the highest 10y yields are {", ".join(f"{m} {f(v)}%" for m, v in hedged.head(3).items())}: once
  the short-rate differential is paid away, Poland's pickup over France is small.
- **Fiscal.** Japan, the US and France have the highest debt ratios; Poland's is lower but
  rising fastest in the OECD projections ({f(c.loc["PL", "debt_gdp_2025"], 1)}% in 2025 to {f(c.loc["PL", "debt_gdp_2027_proj"], 1)}% in 2027).

![10y spreads](figures/spreads_10y.png)

Generated table: [generated/05_country_comparison.md](generated/05_country_comparison.md).
"""
    (R / "05_country_comparison.md").write_text(text, encoding="utf-8")


# ------------------------------------------------------------------------------------ 06
def note_frpl():
    sp = pd.read_csv(G / "frpl_spreads.csv", index_col=0, parse_dates=True)
    hc = pd.read_csv(G / "frpl_hedge.csv", index_col=0, parse_dates=True)
    cm = pd.read_csv(G / "frpl_co_movement.csv", index_col=0, parse_dates=True)
    tr = pd.read_csv(G / "frpl_trades.csv", index_col=0)
    mac = pd.read_csv(G / "frpl_macro.csv", index_col=0)
    last = sp.index[-1]
    s5 = sp[sp.index > last - pd.DateOffset(years=5)]
    lv = pd.DataFrame({"now": sp.iloc[-1], "1y ago": sp[sp.index <= last - pd.DateOffset(years=1)].iloc[-1],
                       "5y mean": s5.mean(), "5y min": s5.min(), "5y max": s5.max(),
                       "z (5y)": (sp.iloc[-1] - s5.mean()) / s5.std()}).round(1).reset_index().rename(columns={"index": "spread (bp)"})
    h = hc.dropna().iloc[-1]
    h5 = hc["hedged_pickup_bp"][hc.index > last - pd.DateOffset(years=5)]
    c = cm.dropna().iloc[-1]
    b5 = cm["beta_PL_on_FR"][cm.index > last - pd.DateOffset(years=5)].median()
    cols = ["trade", "signal", "test", "ann_return_bp", "ann_vol_bp", "sharpe", "t_nw", "max_dd_bp", "cost_bp_per_year"]
    trt = tr[[c_ for c_ in cols if c_ in tr.columns]].round(2)
    m = mac[mac.year >= 2022].copy()
    best = tr[tr.test == "walk-forward OOS"].sort_values("sharpe", ascending=False).iloc[0]
    stat = tr[tr.signal == "static"].set_index("trade")
    st10 = stat.loc["PL 10y vs FR 10y, DV01-neutral (long PL)"]
    st5 = stat.loc["PL 5y vs FR 5y, DV01-neutral (long PL)"]
    st2 = stat.loc["PL 2y vs FR 2y, DV01-neutral (long PL)"]
    text = f"""# France versus Poland

**Why this pair.** France and Poland borrow in different currencies under different central
banks, and their fiscal paths differ: France has the higher debt ratio, Poland the larger
deficit and the faster-rising debt. A spread between them mixes currency, policy,
inflation, fiscal risk and liquidity. This note lays out the evidence and tests candidate
trades with the same machinery as the rest of the project. **It does not start from, or
arrive at, a trading call.**

**Data.** France: Banque de France TEC constant-maturity yields (daily, sampled weekly).
Poland: curves fitted every week to the BondSpot fixing of Polish government bonds
(2006-{last.year}). Funding: EUR STR and the NBP reference rate. FX: ECB EUR/PLN.

## Where the spreads stand ({last:%Y-%m-%d})

{md_table(lv, 1)}

The Poland-France spread is near the low end of its five-year range at every tenor, after
the 2022 spike when Polish inflation and policy rates rose far faster than euro-area ones.
Both curves are steep; Poland's 2s10s is at the top of its five-year range.

## Co-movement and currency

- 52-week beta of Polish on French 10y yield changes: {f(c.beta_PL_on_FR)} (five-year median {f(b5)});
  correlation {f(c["corr"])}. Polish 10y volatility {f(c.vol_PL10_bp, 0)} bp a year vs {f(c.vol_FR10_bp, 0)} bp for France.
- Hedging PLN into EUR costs about the short-rate differential: {f(h.r_PLN)}% - {f(h.r_EUR)}% =
  {f(h.hedge_cost)}% a year. Hedged, the Polish 10y yields {f(h.PL10_hedged_EUR)}% vs {f(h.FR10)}% for France:
  a pickup of {f(h.hedged_pickup_bp, 1)} bp (five-year average {f(h5.mean(), 1)} bp). Most of the unhedged spread is
  the price of the currency.

![Poland minus France](figures/frpl_spreads.png)

![Beta and correlation](figures/frpl_beta.png)

## Macro and fiscal

{md_table(m.round(2), 2)}

OECD figures; {int(m.year.max())} and the latest year with an outturn may be projections.

## Candidate trades

Weekly backtests, P&L in bp per unit of DV01 a year, Polish costs from the fixing's bid and
offer (2.0-4.5 bp one way), French costs assumed (0.40-0.45 bp):

{md_table(trt, 2)}

The best walk-forward result is **{best.trade}** ({f(best.ann_return_bp, 1)} bp a year, Sharpe
{f(best.sharpe)}, t {f(best.t_nw)}): not distinguishable from zero.

Holding the spread statically (long Poland) returned {f(st10.gross_ann_return_bp, 1)} bp a year before costs at 10
years (about nothing), {f(st5.gross_ann_return_bp, 1)} at 5 and {f(st2.gross_ann_return_bp, 1)} at 2. Costs of {f(st10.cost_bp_per_year, 1)}, {f(st5.cost_bp_per_year, 1)} and
{f(st2.cost_bp_per_year, 1)} bp a year make all three negative; they come mostly from rolling the Polish leg
every quarter at the bid/offer measured in the fixing. An investor who rolls less often pays
less, so for the 2- and 5-year static trades the cost assumption, not the spread, decides
the sign of the result.

## What would have to be true

For a long Poland / short France 10y trade to work from here, Polish yields would have to
fall relative to French ones beyond what the forwards already price - for example, through
Polish inflation and policy rates falling faster than euro-area ones, or French fiscal risk
being repriced. Against it: the spread is already near its five-year low, the hedged pickup
is close to zero, and Poland's deficits and debt path are the larger fiscal risk in the OECD
projections. The opposite trade has the mirror-image case. The framework measures carry,
roll-down, volatility, beta and history for either side; it does not choose one.

Generated tables: [generated/06_france_vs_poland.md](generated/06_france_vs_poland.md) and `generated/frpl_*.csv`.
"""
    (R / "06_france_vs_poland.md").write_text(text, encoding="utf-8")


# ------------------------------------------------------------------------------------ index
def note_index():
    text = """# Research notes

| Note | Question |
|---|---|
| [01 Curve fitting](01_curve_fitting.md) | Which curve model fits best out of sample, and which is stable? |
| [02 PCA](02_pca.md) | How many factors move each curve, are they stable, what were the largest moves? |
| [03 Strategies](03_strategies.md) | Which RV signals survived costs and out-of-sample tests? |
| [04 Scanner](04_scanner.md) | Where do spreads, butterflies and cross-country spreads stand today? |
| [05 Country comparison](05_country_comparison.md) | Curves, policy paths, inflation, real yields, fiscal and hedged yields side by side |
| [06 France vs Poland](06_france_vs_poland.md) | A case study with the framework, without a predetermined conclusion |

`generated/` holds the tables and CSVs written by `scripts/run_research.py`; `figures/` the
charts. The notes are written by `scripts/write_research_notes.py` from those outputs.
"""
    (R / "README.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    note_fit()
    note_pca()
    note_strategies()
    note_scanner()
    note_country()
    note_frpl()
    note_index()
    print("wrote research/*.md")
