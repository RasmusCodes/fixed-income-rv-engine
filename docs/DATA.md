# Data

Every number in this project comes from one of the sources below. Nothing is invented or
simulated; where a number is computed here (fitted curves, inferred coupons, breakevens as
differences, PCA) it is labelled *derived*. Classes:

- **official**: an official statistic or official market fixing;
- **estimate**: an official model estimate (central-bank fitted curves) - a model output, not a price;
- **market**: vendor market quotes;
- **derived**: computed in this project from the above.

## Sources

| Id | Provider | Series | Class | Access | Terms / notes |
|---|---|---|---|---|---|
| `ust_par` | U.S. Department of the Treasury | [Daily Treasury Par Yield Curve Rates (CMT)](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve) | official | script | US government work, public domain. Par yields, semiannual bond-equivalent basis, read from a monotone convex spline the Treasury fits to on-the-run securities (since Dec 2021; quasi-cubic Hermite spline before). |
| `ust_real` | U.S. Department of the Treasury | [Daily Treasury Par Real Yield Curve Rates](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_real_yield_curve) | official | script | US government work, public domain. Real par yields on TIPS at 5, 7, 10, 20 and 30 years. |
| `fed_gsw` | Federal Reserve Board (Gurkaynak, Sack and Wright 2007) | [The U.S. Treasury Yield Curve: 1961 to the Present (feds200628)](https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv) | estimate | script | Fed staff research data, free to use with attribution. Svensson parameters and continuously compounded zero, par and forward rates fitted to off-the-run Treasuries; staff research product, not an official statistic. |
| `fed_gsw_tips` | Federal Reserve Board (Gurkaynak, Sack and Wright 2010) | [The TIPS Yield Curve and Inflation Compensation (feds200805)](https://www.federalreserve.gov/data/yield-curve-tables/feds200805.csv) | estimate | script | Fed staff research data, free to use with attribution. Real zero-coupon curve and breakeven inflation from TIPS. |
| `nyfed_sofr` | Federal Reserve Bank of New York | [Secured Overnight Financing Rate (SOFR)](https://markets.newyorkfed.org/api/rates/secured/sofr/search.json) | official | script | NY Fed terms of use; reference rates may be used with attribution. Used as the US funding (repo) rate for carry. |
| `bbk_svensson` | Deutsche Bundesbank | [Term structure of interest rates on listed Federal securities (Svensson method)](https://api.statistiken.bundesbank.de/rest/data/BBSIS/D.I.ZST.ZI.EUR.S1311.B.A604..R.A.A._Z._Z.A) | estimate | script | Bundesbank time series database; free use with source attribution. Zero-coupon yields of German Federal securities at residual maturities 0.5-30 years. |
| `ecb_yc` | European Central Bank | [Euro area yield curves (Svensson parameters, AAA and all central government bonds)](https://data-api.ecb.europa.eu/service/data/YC) | estimate | script | ECB data may be reused with attribution. Continuously compounded Svensson curves. |
| `ecb_estr` | European Central Bank | [Euro short-term rate (EUR STR)](https://data-api.ecb.europa.eu/service/data/EST/B.EU000A2X2A25.WT) | official | script | ECB data may be reused with attribution. Euro funding rate for carry. |
| `bdf_tec` | Banque de France (Webstat), index computed by Euronext | [Taux de l'Echeance Constante (TEC) 1-30 years](https://webstat.banque-france.fr/fr/catalogue/fm/FM.D.FR.EUR.FR2.BB.FRMOYTEC10.HSTA) | official | browser download (Webstat export) | Banque de France Webstat; series source Euronext (EUXT). French constant-maturity OAT yields: actuarial yields interpolated between the two OATs bracketing each maturity; treated as annual-coupon par yields. |
| `boe_glc` | Bank of England | [UK government liability curves (nominal, real, inflation) and SONIA OIS curve](https://www.bankofengland.co.uk/statistics/yield-curves) | estimate | browser download | Bank of England; free use with attribution, no warranty. Spline-based (variable roughness penalty) zero-coupon curves; real and inflation curves from index-linked gilts (1985-); OIS from 2009. |
| `mof_jgb` | Ministry of Finance, Japan | [JGB interest rates (constant maturity, 1-40 years)](https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/index.htm) | official | script | MoF Japan website terms (government standard terms of use, compatible with CC BY 4.0). Semiannual compound yields of JGBs interpolated to constant maturities; treated as semiannual par yields. |
| `bondspot_fixing` | BondSpot S.A. (Treasury BondSpot Poland, GPW group) | [Fixing obligacji - daily fixing of Polish Treasury bonds](https://www.bondspot.pl/fixing_obligacji) | official | script | Public website; raw fixings are not redistributed in this repository, only fitted curves. Bid, offer and fixing prices and yields for each fixed-rate Polish government bond (OK/PS/DS/WS lines). |
| `fred_swaps` | ICE Benchmark Administration via FRED (Federal Reserve Bank of St. Louis) | [ICE Swap Rates DSWP1-DSWP30 (discontinued 2016)](https://fred.stlouisfed.org/graph/fredgraph.csv?id=DSWP1,DSWP2,DSWP3,DSWP4,DSWP5,DSWP7,DSWP10,DSWP30) | market | browser download | ICE data via FRED; historical series no longer updated (ended Oct 2016). USD LIBOR swap rates (fixed vs 3m LIBOR, semiannual 30/360) - used for the historical swap-spread study only. |
| `fred_moodys` | Moody's via FRED | [Moody's Seasoned Aaa and Baa Corporate Bond Yields (DAAA, DBAA)](https://fred.stlouisfed.org/graph/fredgraph.csv?id=DAAA,DBAA) | market | browser download | Moody's data via FRED, attribution required. Yields on seasoned long-maturity corporate bonds (20+ years). |
| `bis_policy` | Bank for International Settlements | [Central bank policy rates (WS_CBPOL)](https://stats.bis.org/api/v1/data/WS_CBPOL) | official | script | BIS terms of use: free with attribution. Policy rates of the Fed, ECB, Bank of England, Bank of Japan and National Bank of Poland. |
| `oecd_mei` | OECD | [Financial market indicators: 3-month interbank and long-term interest rates](https://sdmx.oecd.org/public/rest/data) | official | script | OECD data, CC BY 4.0. 3-month interbank rates and long-term (10y) government yields for all six countries. |
| `bis_cpi` | Bank for International Settlements | [Consumer prices, long series (WS_LONG_CPI), year-on-year change](https://stats.bis.org/api/v1/data/WS_LONG_CPI) | official | script | BIS terms of use: free with attribution. National CPIs compiled by the BIS; used for inflation and ex-post real yields. |
| `ecb_fx` | European Central Bank | [Euro foreign exchange reference rates (EXR)](https://data-api.ecb.europa.eu/service/data/EXR) | official | script | ECB data may be reused with attribution. EUR/PLN, EUR/USD, EUR/GBP, EUR/JPY for FX volatility and hedged yields. |
| `oecd_eo` | OECD Economic Outlook | [General government gross debt and net lending (% of GDP)](https://sdmx.oecd.org/public/rest/data) | official | script | OECD data, CC BY 4.0. Fiscal inputs to the country comparison; latest years are OECD projections. |

## Coverage of the processed panels (as built)

| Panel | Description | First | Last | Rows | Columns |
|---|---|---|---|---:|---:|
| `us_par` | US Treasury par yields (CMT) | 1990-01-02 | 2026-11-20 | 9,228 | 14 |
| `us_real` | US Treasury real par yields | 2003-01-02 | 2026-11-20 | 5,976 | 5 |
| `us_gsw_zero` | GSW nominal zero curve | 1961-06-14 | 2026-11-13 | 16,318 | 30 |
| `us_tips_real_zero` | GSW TIPS real zero curve | 1999-01-04 | 2026-11-13 | 6,961 | 19 |
| `us_sofr` | SOFR | 2018-04-02 | 2026-11-19 | 2,157 | 1 |
| `de_zero` | Bundesbank zero curve | 1997-08-07 | 2026-11-20 | 7,436 | 60 |
| `de_params` | Bundesbank Svensson parameters | 1997-08-07 | 2026-11-20 | 7,436 | 6 |
| `ea_aaa_params` | ECB AAA Svensson parameters | 2004-09-06 | 2026-11-19 | 5,678 | 6 |
| `ea_all_params` | ECB all-issuer Svensson parameters | 2004-09-06 | 2026-11-19 | 5,678 | 6 |
| `ea_estr` | EUR STR | 2019-10-01 | 2026-11-19 | 1,829 | 1 |
| `fr_tec` | Banque de France TEC | 2004-11-03 | 2026-11-20 | 5,645 | 10 |
| `uk_nominal` | BoE nominal spot curve | 1979-01-02 | 2026-11-19 | 12,104 | 80 |
| `uk_real` | BoE real spot curve | 1985-01-02 | 2026-11-19 | 10,586 | 76 |
| `uk_inflation` | BoE implied inflation spot curve | 1985-01-02 | 2026-11-19 | 10,586 | 76 |
| `uk_ois` | BoE SONIA OIS spot curve | 2009-01-02 | 2026-11-19 | 4,518 | 108 |
| `jp_par` | MoF JGB yields | 1974-09-24 | 2026-11-19 | 13,343 | 15 |
| `pl_par` | Polish par curve (fitted) | 2006-01-06 | 2026-11-20 | 1,090 | 9 |
| `us_swaps_ice` | ICE USD swap rates (FRED) | 2000-07-03 | 2016-10-28 | 4,081 | 8 |
| `us_moodys` | Moody's Aaa/Baa (FRED) | 1983-01-03 | 2026-11-19 | 11,016 | 2 |
| `policy_rates` | BIS policy rates | 1990-01-01 | 2026-11-17 | 13,470 | 5 |
| `cpi_yoy` | BIS CPI, y/y | 1990-01-31 | 2026-09-30 | 441 | 6 |
| `oecd_rates` | OECD 3m and 10y rates | 1990-01-31 | 2026-10-31 | 442 | 12 |
| `oecd_fiscal` | OECD debt and net lending | 1995-12-31 | 2027-12-31 | 33 | 16 |
| `fx_eur` | ECB EUR reference rates | 1999-01-04 | 2026-11-20 | 7,141 | 4 |

## Notes and caveats

- **Compounding** was verified from the data: Bundesbank, Fed GSW and ECB yields reproduce from their
  Svensson parameters only with continuous compounding; the Bank of England's one-month OIS spot equals the
  continuous equivalent of SONIA. See docs/METHODOLOGY.md section 7.
- **US 30-year gap**: the Treasury did not publish a 30-year CMT between February 2002 and February 2006.
  Changes are never computed across that gap.
- **UK long end**: the Bank of England curve extends beyond 25 years only from January 2016, so UK work that
  needs the 30-year point starts then.
- **French TEC** yields are interpolated yields of the two OATs bracketing each maturity; they are treated as
  annual-coupon par yields. The series is computed by Euronext and published by the Banque de France.
- **Japanese MoF** yields are treated as semiannual par yields.
- **Poland**: the BondSpot fixing is sampled weekly (Friday, or the last earlier trading day). Fixed-rate lines
  only (OK, PS, DS, WS); coupons are inferred from price and yield and checked; settlement T+2 business days
  (weekends only, no Polish holiday calendar). Recently the longest fixed-rate bond in the fixing has about
  9.4 years left, so the 10-year point is extrapolated by up to one year; longer points are left empty.
  Measured one-way costs (half bid/offer, bp): {'2': 4.5, '5': 2.5, '10': 2.0}.
- **Inflation**: BIS consumer-price series. The OECD prices dataflow was checked first, but in November 2026
  its French and Polish series stopped at December 2025 and the Japanese one at June 2021.
- **Swaps**: ICE USD swap rates are fixed vs 3-month LIBOR and end in October 2016; their floating leg is
  financed at the bill rate in the backtests (LIBOR is not in the data), which understates the carry of a long
  swap-spread position by the LIBOR-bill spread. UK swap spreads use the BoE SONIA OIS curve.
- **Funding**: SOFR (3-month bill before April 2018), EUR STR (6-month Bund zero rate before October 2019), Bank
  Rate, BoJ and NBP policy rates (BIS).
- **Fiscal**: OECD Economic Outlook; years after the latest outturn are OECD projections.
- **Futures**: CME settlement prices refuse scripts and no other free source was found, so futures basis is
  analytics only.
- **IMF** data (debt, inflation) and the **UK DMO** gilt prices block scripts; they are not used.

## Reproducing

`python scripts/fetch_data.py` downloads everything available to scripts into `data/raw/<source>/` with a
`_manifest.json` (URL, time, size) and writes parsed panels to `data/processed/`. Sources that refuse scripts are
read from `data/inbox/` (see docs/DOWNLOADS.md). `python scripts/collect_poland.py` collects the fixings (about
1,100 pages, resumable) and fits the Polish curves.
