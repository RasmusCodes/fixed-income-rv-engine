"""Write docs/DATA.md from the source registry and the processed panels (coverage, size)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from firv.data.sources import SOURCES  # noqa: E402

PANELS = [
    ("us_par", "US Treasury par yields (CMT)"), ("us_real", "US Treasury real par yields"),
    ("us_gsw_zero", "GSW nominal zero curve"), ("us_tips_real_zero", "GSW TIPS real zero curve"),
    ("us_sofr", "SOFR"), ("de_zero", "Bundesbank zero curve"), ("de_params", "Bundesbank Svensson parameters"),
    ("ea_aaa_params", "ECB AAA Svensson parameters"), ("ea_all_params", "ECB all-issuer Svensson parameters"),
    ("ea_estr", "EUR STR"), ("fr_tec", "Banque de France TEC"), ("uk_nominal", "BoE nominal spot curve"),
    ("uk_real", "BoE real spot curve"), ("uk_inflation", "BoE implied inflation spot curve"),
    ("uk_ois", "BoE SONIA OIS spot curve"), ("jp_par", "MoF JGB yields"), ("pl_par", "Polish par curve (fitted)"),
    ("us_swaps_ice", "ICE USD swap rates (FRED)"), ("us_moodys", "Moody's Aaa/Baa (FRED)"),
    ("policy_rates", "BIS policy rates"), ("cpi_yoy", "BIS CPI, y/y"), ("oecd_rates", "OECD 3m and 10y rates"),
    ("oecd_fiscal", "OECD debt and net lending"), ("fx_eur", "ECB EUR reference rates"),
]


def main():
    proc = ROOT / "data" / "processed"
    lines = ["# Data", "",
             "Every number in this project comes from one of the sources below. Nothing is invented or",
             "simulated; where a number is computed here (fitted curves, inferred coupons, breakevens as",
             "differences, PCA) it is labelled *derived*. Classes:", "",
             "- **official**: an official statistic or official market fixing;",
             "- **estimate**: an official model estimate (central-bank fitted curves) - a model output, not a price;",
             "- **market**: vendor market quotes;",
             "- **derived**: computed in this project from the above.", "",
             "## Sources", "",
             "| Id | Provider | Series | Class | Access | Terms / notes |", "|---|---|---|---|---|---|"]
    for sid, s in SOURCES.items():
        lines.append(f"| `{sid}` | {s['provider']} | [{s['title']}]({s['url']}) | {s['class']} | {s['access']} | "
                     f"{s['terms']}. {s['notes']} |")
    lines += ["", "## Coverage of the processed panels (as built)", "",
              "| Panel | Description | First | Last | Rows | Columns |", "|---|---|---|---|---:|---:|"]
    for name, desc in PANELS:
        p = proc / f"{name}.parquet"
        if not p.exists():
            lines.append(f"| `{name}` | {desc} | not built | | | |")
            continue
        df = pd.read_parquet(p)
        df.index = pd.to_datetime(df.index)
        df = df.dropna(how="all")
        lines.append(f"| `{name}` | {desc} | {df.index.min():%Y-%m-%d} | {df.index.max():%Y-%m-%d} | {len(df):,} | {df.shape[1]} |")
    costs = json.loads((proc / "pl_costs.json").read_text()) if (proc / "pl_costs.json").exists() else {}
    lines += ["", "## Notes and caveats", "",
              "- **Compounding** was verified from the data: Bundesbank, Fed GSW and ECB yields reproduce from their",
              "  Svensson parameters only with continuous compounding; the Bank of England's one-month OIS spot equals the",
              "  continuous equivalent of SONIA. See docs/METHODOLOGY.md section 7.",
              "- **US 30-year gap**: the Treasury did not publish a 30-year CMT between February 2002 and February 2006.",
              "  Changes are never computed across that gap.",
              "- **UK long end**: the Bank of England curve extends beyond 25 years only from January 2016, so UK work that",
              "  needs the 30-year point starts then.",
              "- **French TEC** yields are interpolated yields of the two OATs bracketing each maturity; they are treated as",
              "  annual-coupon par yields. The series is computed by Euronext and published by the Banque de France.",
              "- **Japanese MoF** yields are treated as semiannual par yields.",
              "- **Poland**: the BondSpot fixing is sampled weekly (Friday, or the last earlier trading day). Fixed-rate lines",
              "  only (OK, PS, DS, WS); coupons are inferred from price and yield and checked; settlement T+2 business days",
              "  (weekends only, no Polish holiday calendar). Recently the longest fixed-rate bond in the fixing has about",
              "  9.4 years left, so the 10-year point is extrapolated by up to one year; longer points are left empty.",
              f"  Measured one-way costs (half bid/offer, bp): {costs.get('one_way_bp_by_tenor', 'n/a')}.",
              "- **Inflation**: BIS consumer-price series. The OECD prices dataflow was checked first, but in November 2026",
              "  its French and Polish series stopped at December 2025 and the Japanese one at June 2021.",
              "- **Swaps**: ICE USD swap rates are fixed vs 3-month LIBOR and end in October 2016; their floating leg is",
              "  financed at the bill rate in the backtests (LIBOR is not in the data), which understates the carry of a long",
              "  swap-spread position by the LIBOR-bill spread. UK swap spreads use the BoE SONIA OIS curve.",
              "- **Funding**: SOFR (3-month bill before April 2018), EUR STR (6-month Bund zero rate before October 2019), Bank",
              "  Rate, BoJ and NBP policy rates (BIS).",
              "- **Fiscal**: OECD Economic Outlook; years after the latest outturn are OECD projections.",
              "- **Futures**: CME settlement prices refuse scripts and no other free source was found, so futures basis is",
              "  analytics only.",
              "- **IMF** data (debt, inflation) and the **UK DMO** gilt prices block scripts; they are not used.", "",
              "## Reproducing", "",
              "`python scripts/fetch_data.py` downloads everything available to scripts into `data/raw/<source>/` with a",
              "`_manifest.json` (URL, time, size) and writes parsed panels to `data/processed/`. Sources that refuse scripts are",
              "read from `data/inbox/` (see docs/DOWNLOADS.md). `python scripts/collect_poland.py` collects the fixings (about",
              "1,100 pages, resumable) and fits the Polish curves.", ""]
    (ROOT / "docs" / "DATA.md").write_text("\n".join(lines), encoding="utf-8")
    print("wrote docs/DATA.md")


if __name__ == "__main__":
    main()
