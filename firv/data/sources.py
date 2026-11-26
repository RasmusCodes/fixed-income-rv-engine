"""Registry of every data source: who publishes it, what kind of number it is, and how it
is obtained. The classification is shown next to every number in the docs and the demo.

Classes:
  official   - official statistic or official fixing published by a government body,
               central bank or regulated market operator (e.g. Treasury par yields, the
               BondSpot fixing, BIS policy rates);
  estimate   - official model estimate (central-bank fitted curves: GSW, Bundesbank,
               ECB, Bank of England); a model output, not a traded price;
  market     - market quotes from a data vendor (ICE swap rates via FRED, Moody's yields);
  derived    - computed in this project from the above (fitted Polish curves, PCA,
               breakevens as differences, inferred coupons);
  synthetic  - made-up inputs for illustration only (always labelled in the demo).
"""
from __future__ import annotations

SOURCES = {
    "ust_par": {
        "provider": "U.S. Department of the Treasury",
        "title": "Daily Treasury Par Yield Curve Rates (CMT)",
        "url": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve",
        "class": "official", "access": "script", "freq": "daily", "start": "1990-01-02",
        "terms": "US government work, public domain",
        "notes": "Par yields, semiannual bond-equivalent basis, read from a monotone convex spline the Treasury fits to on-the-run securities (since Dec 2021; quasi-cubic Hermite spline before).",
    },
    "ust_real": {
        "provider": "U.S. Department of the Treasury",
        "title": "Daily Treasury Par Real Yield Curve Rates",
        "url": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_real_yield_curve",
        "class": "official", "access": "script", "freq": "daily", "start": "2003-01-02",
        "terms": "US government work, public domain",
        "notes": "Real par yields on TIPS at 5, 7, 10, 20 and 30 years.",
    },
    "fed_gsw": {
        "provider": "Federal Reserve Board (Gurkaynak, Sack and Wright 2007)",
        "title": "The U.S. Treasury Yield Curve: 1961 to the Present (feds200628)",
        "url": "https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv",
        "class": "estimate", "access": "script", "freq": "daily", "start": "1961-06-14",
        "terms": "Fed staff research data, free to use with attribution",
        "notes": "Svensson parameters and continuously compounded zero, par and forward rates fitted to off-the-run Treasuries; staff research product, not an official statistic.",
    },
    "fed_gsw_tips": {
        "provider": "Federal Reserve Board (Gurkaynak, Sack and Wright 2010)",
        "title": "The TIPS Yield Curve and Inflation Compensation (feds200805)",
        "url": "https://www.federalreserve.gov/data/yield-curve-tables/feds200805.csv",
        "class": "estimate", "access": "script", "freq": "daily", "start": "1999-01-04",
        "terms": "Fed staff research data, free to use with attribution",
        "notes": "Real zero-coupon curve and breakeven inflation from TIPS.",
    },
    "nyfed_sofr": {
        "provider": "Federal Reserve Bank of New York",
        "title": "Secured Overnight Financing Rate (SOFR)",
        "url": "https://markets.newyorkfed.org/api/rates/secured/sofr/search.json",
        "class": "official", "access": "script", "freq": "daily", "start": "2018-04-02",
        "terms": "NY Fed terms of use; reference rates may be used with attribution",
        "notes": "Used as the US funding (repo) rate for carry.",
    },
    "bbk_svensson": {
        "provider": "Deutsche Bundesbank",
        "title": "Term structure of interest rates on listed Federal securities (Svensson method)",
        "url": "https://api.statistiken.bundesbank.de/rest/data/BBSIS/D.I.ZST.ZI.EUR.S1311.B.A604..R.A.A._Z._Z.A",
        "class": "estimate", "access": "script", "freq": "daily", "start": "1997-08-07",
        "terms": "Bundesbank time series database; free use with source attribution",
        "notes": "Zero-coupon yields of German Federal securities at residual maturities 0.5-30 years.",
    },
    "ecb_yc": {
        "provider": "European Central Bank",
        "title": "Euro area yield curves (Svensson parameters, AAA and all central government bonds)",
        "url": "https://data-api.ecb.europa.eu/service/data/YC",
        "class": "estimate", "access": "script", "freq": "daily", "start": "2004-09-06",
        "terms": "ECB data may be reused with attribution",
        "notes": "Continuously compounded Svensson curves.",
    },
    "ecb_estr": {
        "provider": "European Central Bank",
        "title": "Euro short-term rate (EUR STR)",
        "url": "https://data-api.ecb.europa.eu/service/data/EST/B.EU000A2X2A25.WT",
        "class": "official", "access": "script", "freq": "daily", "start": "2019-10-01",
        "terms": "ECB data may be reused with attribution",
        "notes": "Euro funding rate for carry.",
    },
    "bdf_tec": {
        "provider": "Banque de France (Webstat), index computed by Euronext",
        "title": "Taux de l'Echeance Constante (TEC) 1-30 years",
        "url": "https://webstat.banque-france.fr/fr/catalogue/fm/FM.D.FR.EUR.FR2.BB.FRMOYTEC10.HSTA",
        "class": "official", "access": "browser download (Webstat export)", "freq": "daily", "start": "2004-11-03",
        "terms": "Banque de France Webstat; series source Euronext (EUXT)",
        "notes": "French constant-maturity OAT yields: actuarial yields interpolated between the two OATs bracketing each maturity; treated as annual-coupon par yields.",
    },
    "boe_glc": {
        "provider": "Bank of England",
        "title": "UK government liability curves (nominal, real, inflation) and SONIA OIS curve",
        "url": "https://www.bankofengland.co.uk/statistics/yield-curves",
        "class": "estimate", "access": "browser download", "freq": "daily", "start": "1979-01-02",
        "terms": "Bank of England; free use with attribution, no warranty",
        "notes": "Spline-based (variable roughness penalty) zero-coupon curves; real and inflation curves from index-linked gilts (1985-); OIS from 2009.",
    },
    "mof_jgb": {
        "provider": "Ministry of Finance, Japan",
        "title": "JGB interest rates (constant maturity, 1-40 years)",
        "url": "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/index.htm",
        "class": "official", "access": "script", "freq": "daily", "start": "1974-09-24",
        "terms": "MoF Japan website terms (government standard terms of use, compatible with CC BY 4.0)",
        "notes": "Semiannual compound yields of JGBs interpolated to constant maturities; treated as semiannual par yields.",
    },
    "bondspot_fixing": {
        "provider": "BondSpot S.A. (Treasury BondSpot Poland, GPW group)",
        "title": "Fixing obligacji - daily fixing of Polish Treasury bonds",
        "url": "https://www.bondspot.pl/fixing_obligacji",
        "class": "official", "access": "script", "freq": "daily (sampled weekly here)", "start": "2006-01-03",
        "terms": "Public website; raw fixings are not redistributed in this repository, only fitted curves",
        "notes": "Bid, offer and fixing prices and yields for each fixed-rate Polish government bond (OK/PS/DS/WS lines).",
    },
    "fred_swaps": {
        "provider": "ICE Benchmark Administration via FRED (Federal Reserve Bank of St. Louis)",
        "title": "ICE Swap Rates DSWP1-DSWP30 (discontinued 2016)",
        "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DSWP1,DSWP2,DSWP3,DSWP4,DSWP5,DSWP7,DSWP10,DSWP30",
        "class": "market", "access": "browser download", "freq": "daily", "start": "2000-07-03",
        "terms": "ICE data via FRED; historical series no longer updated (ended Oct 2016)",
        "notes": "USD LIBOR swap rates (fixed vs 3m LIBOR, semiannual 30/360) - used for the historical swap-spread study only.",
    },
    "fred_moodys": {
        "provider": "Moody's via FRED",
        "title": "Moody's Seasoned Aaa and Baa Corporate Bond Yields (DAAA, DBAA)",
        "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DAAA,DBAA",
        "class": "market", "access": "browser download", "freq": "daily", "start": "1983-01-03",
        "terms": "Moody's data via FRED, attribution required",
        "notes": "Yields on seasoned long-maturity corporate bonds (20+ years).",
    },
    "bis_policy": {
        "provider": "Bank for International Settlements",
        "title": "Central bank policy rates (WS_CBPOL)",
        "url": "https://stats.bis.org/api/v1/data/WS_CBPOL",
        "class": "official", "access": "script", "freq": "daily", "start": "1946-01-01",
        "terms": "BIS terms of use: free with attribution",
        "notes": "Policy rates of the Fed, ECB, Bank of England, Bank of Japan and National Bank of Poland.",
    },
    "oecd_mei": {
        "provider": "OECD",
        "title": "Financial market indicators: 3-month interbank and long-term interest rates",
        "url": "https://sdmx.oecd.org/public/rest/data",
        "class": "official", "access": "script", "freq": "monthly", "start": "1990-01",
        "terms": "OECD data, CC BY 4.0",
        "notes": "3-month interbank rates and long-term (10y) government yields for all six countries.",
    },
    "bis_cpi": {
        "provider": "Bank for International Settlements",
        "title": "Consumer prices, long series (WS_LONG_CPI), year-on-year change",
        "url": "https://stats.bis.org/api/v1/data/WS_LONG_CPI",
        "class": "official", "access": "script", "freq": "monthly", "start": "1990-01",
        "terms": "BIS terms of use: free with attribution",
        "notes": "National CPIs compiled by the BIS; used for inflation and ex-post real yields.",
    },
    "ecb_fx": {
        "provider": "European Central Bank",
        "title": "Euro foreign exchange reference rates (EXR)",
        "url": "https://data-api.ecb.europa.eu/service/data/EXR",
        "class": "official", "access": "script", "freq": "daily", "start": "1999-01-04",
        "terms": "ECB data may be reused with attribution",
        "notes": "EUR/PLN, EUR/USD, EUR/GBP, EUR/JPY for FX volatility and hedged yields.",
    },
    "oecd_eo": {
        "provider": "OECD Economic Outlook",
        "title": "General government gross debt and net lending (% of GDP)",
        "url": "https://sdmx.oecd.org/public/rest/data",
        "class": "official", "access": "script", "freq": "annual", "start": "1995",
        "terms": "OECD data, CC BY 4.0",
        "notes": "Fiscal inputs to the country comparison; latest years are OECD projections.",
    },
}


def describe(source_id: str) -> str:
    s = SOURCES[source_id]
    return f"{s['provider']}: {s['title']} [{s['class']}]"
