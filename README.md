# fixed-income-rv-engine

A research platform for government bond yield curves and relative-value trades: curve
fitting, risk, DV01-neutral trade construction, a relative-value scanner, backtests and a
cross-country comparison for the United States, Germany, France, Poland, the United Kingdom
and Japan.

**Interactive terminal:** <https://rasmuscodes.github.io/projects/fixed-income/> (curves are
fitted and trades priced in the browser by a JavaScript port of this engine, checked against
the Python value by value).

## What is in it

| Area | Module | What it does |
|---|---|---|
| Curve models | `firv/curves/` | Nelson-Siegel, Nelson-Siegel-Svensson, smoothing forward spline (B-spline with a roughness penalty), natural cubic spline, bootstrapping from par yields, zero, forward and par curves |
| Fitting | `firv/curves/fitting.py` | One interface for zero rates, par yields and individual bonds (cash flows and prices); in-sample and leave-one-out errors |
| PCA | `firv/curves/pca.py` | PCA of curve changes, rolling-window stability, decomposition of any curve move into level, slope and curvature |
| Bonds | `firv/bonds.py` | Dated bonds: schedules, accrued interest, street-convention yields, duration, convexity, DV01, z-spreads, implied coupons |
| Instruments | `firv/instruments.py` | Constant-maturity bonds, swaps, linkers, credit bonds, bond futures (CTD approximation), conversion factors |
| Risk | `firv/risk.py` | Yield DV01, zero-curve DV01, key-rate DV01, duration and convexity, spread DV01, inflation DV01, carry and roll-down, scenario P&L by full revaluation, risk-adjusted comparison |
| Trades | `firv/strategies.py` | Steepeners and flatteners, butterflies (50/50, regression or PCA weights), PCA factor trades, cross-country spreads (DV01 or beta hedged), swap spreads, futures basis (gross/net basis, implied repo), breakevens, credit, carry and roll-down ranking |
| Backtests | `firv/backtest.py` | DV01-unit P&L with carry, roll-down and convexity; transaction and roll costs; in-sample/out-of-sample split; walk-forward parameter selection |
| Scanner | `firv/scanner.py` | Every curve spread, butterfly, cross-country spread, swap spread, breakeven and credit spread against its own history, with carry, volatility and PCA rich/cheap |
| Research | `firv/research/` | Curve-fit study, PCA study, strategy study, country comparison, France vs Poland case study |
| Data | `firv/data/` | Loaders for every source with a raw-file cache and provenance manifest |
| Terminal | `web/` | `firv.js` (engine port), `terminal.js`, exported weekly data |

## Results in brief

Full notes with tables and charts are in [research/](research/README.md).

- **Curve fitting** (5,608 fits, month ends since 1990, US/France/Japan par yields and
  Polish bonds): out of sample (leave one out), Svensson had the lowest error in the US
  (6.3 bp), France (3.3 bp) and Poland (4.5 bp); the cubic spline in Japan (2.6 bp).
  Nelson-Siegel, with a single hump, had the highest out-of-sample error in the US, France
  and Japan. The smoothing spline added the least day-to-day noise at unobserved maturities
  in the US, France and Japan, in every regime.
- **PCA**: level explains 80-90% of daily curve changes since 2000, slope 8-13%, curvature
  1-3%. Level and slope loadings are stable across two-year windows (median cosine
  0.96-1.00); curvature is not (minimum cosine 0.20 in Germany).
- **Strategies**: z-score mean reversion of curve slopes lost money out of sample in every
  market (US 2s10s walk-forward Sharpe -0.43, Newey-West t -2.6); butterflies and
  cross-country 10y spreads were close to zero or negative after costs, and Polish trades did
  not cover the bid/offer measured in the fixing. The one signal that clears a multiple-testing
  haircut is mean reversion of the US 10y swap spread (2004-2016 walk-forward Sharpe 0.50,
  t 3.8, on discontinued LIBOR swap data).
- **France vs Poland** (November 2026): the 10y spread is 136 bp, near its five-year low of
  130 bp; hedged into euros the Polish 10y yields only about 5 bp more than the French 10y.
  None of the candidate spread trades earned a reliable return historically. The case study
  documents the evidence and does not make a call.

## Data

All yields come from documented sources; nothing is invented or simulated. Every source,
its classification and how it is obtained are listed in [docs/DATA.md](docs/DATA.md).

| Market | Source | Class | Frequency, coverage |
|---|---|---|---|
| United States | U.S. Treasury par yield curve (CMT), real yield curve; Fed GSW zero/TIPS curves | official / official estimate | daily, 1990- (GSW 1961-) |
| Germany | Deutsche Bundesbank Svensson zero curve and parameters | official estimate | daily, 1997- |
| France | Banque de France TEC constant-maturity OAT yields (Euronext index) | official | daily, 2004- |
| Poland | BondSpot fixing of Polish government bonds; curves fitted in this project | official fixing, derived curve | weekly sample, 2006- |
| United Kingdom | Bank of England nominal, real and inflation curves, SONIA OIS curve | official estimate | daily, 1979- (OIS 2009-) |
| Japan | Ministry of Finance JGB constant-maturity yields | official | daily, 1974- |
| Euro area | ECB AAA and all-issuer Svensson curves, EUR STR | official estimate / official | daily, 2004- |
| Macro | BIS policy rates and CPI, OECD rates and fiscal balances, NY Fed SOFR, ECB FX | official | daily to annual |
| Swaps, credit | ICE USD swap rates 2000-2016 and Moody's Aaa/Baa via FRED | market quotes | daily |

**Not in this repository:** raw downloads, the BondSpot fixings (only fitted curves and
residual statistics are published), the ICE and Moody's series (vendor data), and the files
that sources refusing scripts require downloading by hand (Bank of England, Banque de
France, FRED: see [docs/DOWNLOADS.md](docs/DOWNLOADS.md); save them in `data/inbox/`).
`web/data/` holds the weekly samples the terminal needs, with attribution.

## Running it

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt        # numpy, pandas, scipy, ...
.venv\Scripts\python scripts\fetch_data.py           # official sources by script
.venv\Scripts\python scripts\collect_poland.py       # weekly BondSpot fixings + Polish curves
.venv\Scripts\python scripts\run_research.py         # studies -> research/generated, figures
.venv\Scripts\python scripts\export_web.py           # terminal data -> web/data
.venv\Scripts\python -m pytest                       # unit tests (data tests skip without data)
```

`scripts/make_golden.py` writes reference values for the JavaScript port and
`web/test/selftest.html` checks `firv.js` against them (open it in a browser, or run
`scripts/run_js_selftest.ps1`, which prints the page to PDF with headless Edge).

## Conventions

Rates are decimals inside the library, times in years, zero rates continuously compounded.
DV01 is the value gained when yields fall 1 bp. Trades are sized by **yield DV01** (per bp
of each instrument's own yield, the street convention); risk aggregation, key rates and
scenarios use the **zero curve** (per bp of continuously compounded zero rates). For a bond
the two differ by about (1 + y/f); see [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Testing

`pytest` covers day counts, bond analytics against finite differences, curve models
(recovery of known curves from zero, par and bond data), bootstrapping, PCA (including data
gaps), DV01/key-rate identities, trade construction, carry and roll, scenarios, conversion
factors and futures basis. The JavaScript port is checked against Python on 53 values
(`node web/test/run_node.js`, or `web/test/selftest.html` in a browser); CI runs both on every push.

## Limits

- Constant-maturity backtests approximate holding real bonds; they ignore repo specials,
  on-the-run premia and auction cycles, and the cost inputs outside Poland are assumptions.
- No futures prices are freely available, so the basis module is analytics only (fair
  futures from the CTD and repo, implied repo for a given price); it is not backtested.
- The Polish curve stops at about 10 years in recent years: the fixing has had no longer
  fixed-rate bonds.
- Swap data are LIBOR swaps that end in 2016; UK swap spreads use the BoE OIS curve.

## License

MIT, see [LICENSE](LICENSE). Data belong to their publishers; see docs/DATA.md for terms.
