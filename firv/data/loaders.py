"""Loaders for every source in :mod:`firv.data.sources`.

Each ``load_*`` function returns a :class:`Panel`: a DataFrame of yields in percent
(dates x tenors in years) plus what kind of rate it is. Raw downloads are cached by
:func:`firv.data.http.fetch`; parsed panels are cached as parquet in data/processed.
"""
from __future__ import annotations

import datetime as dt
import io
import json
import re
import zipfile
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .http import PROCESSED, fetch, inbox_file


@dataclass
class Panel:
    name: str
    data: pd.DataFrame            # dates x tenors (float years), percent
    kind: str                     # 'par' | 'zero' | 'ytm' | 'rate' | 'params'
    freq: int = 0                 # compounding: 0 = continuous, 1 annual, 2 semiannual
    source: str = ""
    currency: str = ""
    meta: dict = field(default_factory=dict)

    def save(self):
        PROCESSED.mkdir(parents=True, exist_ok=True)
        df = self.data.copy()
        df.columns = [str(c) for c in df.columns]
        df.to_parquet(PROCESSED / f"{self.name}.parquet")
        info = {"name": self.name, "kind": self.kind, "freq": self.freq, "source": self.source,
                "currency": self.currency, "meta": self.meta,
                "columns_numeric": all(_is_num(c) for c in self.data.columns)}
        (PROCESSED / f"{self.name}.json").write_text(json.dumps(info, indent=1, default=str))

    @classmethod
    def load(cls, name: str) -> "Panel":
        info = json.loads((PROCESSED / f"{name}.json").read_text())
        df = pd.read_parquet(PROCESSED / f"{name}.parquet")
        if info.get("columns_numeric"):
            df.columns = [float(c) for c in df.columns]
        df.index = pd.to_datetime(df.index)
        return cls(info["name"], df, info["kind"], info["freq"], info["source"], info["currency"],
                   info.get("meta", {}))


def _is_num(x) -> bool:
    try:
        float(x)
        return True
    except (TypeError, ValueError):
        return False


def cached(name: str) -> Panel | None:
    p = PROCESSED / f"{name}.parquet"
    return Panel.load(name) if p.exists() else None


# =============================================================================== United States
UST_TENORS = {"1 Mo": 1 / 12, "1.5 Month": 1.5 / 12, "2 Mo": 2 / 12, "3 Mo": 0.25, "4 Mo": 4 / 12,
              "6 Mo": 0.5, "1 Yr": 1.0, "2 Yr": 2.0, "3 Yr": 3.0, "5 Yr": 5.0, "7 Yr": 7.0,
              "10 Yr": 10.0, "20 Yr": 20.0, "30 Yr": 30.0}
UST_REAL_TENORS = {"5 YR": 5.0, "7 YR": 7.0, "10 YR": 10.0, "20 YR": 20.0, "30 YR": 30.0}


def _treasury_year(kind: str, year: int) -> pd.DataFrame:
    url = (f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
           f"daily-treasury-rates.csv/{year}/all")
    params = {"type": kind, "field_tdr_date_value": str(year), "page": "", "_format": "csv"}
    this_year = dt.date.today().year
    path = fetch("ust", f"{kind}_{year}.csv", url, params,
                 max_age_days=0.5 if year >= this_year else 3650)
    return pd.read_csv(path)


def load_us_par(start_year: int = 1990) -> Panel:
    frames = []
    for y in range(start_year, dt.date.today().year + 1):
        frames.append(_treasury_year("daily_treasury_yield_curve", y))
    df = pd.concat(frames, ignore_index=True)
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
    df = df.set_index("Date").sort_index()
    df = df[[c for c in UST_TENORS if c in df.columns]].rename(columns=UST_TENORS)
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df[~df.index.duplicated(keep="last")]
    return Panel("us_par", df, "par", 2, "ust_par", "USD")


def load_us_real(start_year: int = 2003) -> Panel:
    frames = [_treasury_year("daily_treasury_real_yield_curve", y)
              for y in range(start_year, dt.date.today().year + 1)]
    df = pd.concat(frames, ignore_index=True)
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
    df = df.set_index("Date").sort_index()
    df = df[[c for c in UST_REAL_TENORS if c in df.columns]].rename(columns=UST_REAL_TENORS)
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df[~df.index.duplicated(keep="last")]
    return Panel("us_real", df, "par", 2, "ust_real", "USD")


def _read_fed_csv(path) -> pd.DataFrame:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("Date,"))
    df = pd.read_csv(io.StringIO("\n".join(lines[start:])))
    df["Date"] = pd.to_datetime(df["Date"])
    return df.set_index("Date").sort_index().apply(pd.to_numeric, errors="coerce")


def load_gsw() -> tuple[Panel, Panel]:
    """GSW nominal zero curve (cont. comp., %) at 1..30y and the Svensson parameters."""
    path = fetch("fed", "feds200628.csv", "https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv",
                 max_age_days=3)
    df = _read_fed_csv(path)
    zcols = {f"SVENY{n:02d}": float(n) for n in range(1, 31)}
    zeros = df[[c for c in zcols if c in df.columns]].rename(columns=zcols)
    params = df[["BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2"]]
    return (Panel("us_gsw_zero", zeros, "zero", 0, "fed_gsw", "USD"),
            Panel("us_gsw_params", params, "params", 0, "fed_gsw", "USD"))


def load_gsw_tips() -> tuple[Panel, Panel]:
    path = fetch("fed", "feds200805.csv", "https://www.federalreserve.gov/data/yield-curve-tables/feds200805.csv",
                 max_age_days=3)
    df = _read_fed_csv(path)
    zcols = {f"TIPSY{n:02d}": float(n) for n in range(2, 21)}
    real = df[[c for c in zcols if c in df.columns]].rename(columns=zcols)
    bcols = {f"BKEVEN{n:02d}": float(n) for n in range(2, 21)}
    bke = df[[c for c in bcols if c in df.columns]].rename(columns=bcols)
    return (Panel("us_tips_real_zero", real, "zero", 0, "fed_gsw_tips", "USD"),
            Panel("us_tips_breakeven", bke, "zero", 0, "fed_gsw_tips", "USD"))


def load_sofr() -> Panel:
    url = "https://markets.newyorkfed.org/api/rates/secured/sofr/search.json"
    params = {"startDate": "2018-04-02", "endDate": dt.date.today().isoformat()}
    path = fetch("nyfed", "sofr.json", url, params, max_age_days=0.5)
    js = json.loads(path.read_text())
    rows = [(r["effectiveDate"], r["percentRate"]) for r in js["refRates"]]
    s = pd.Series({pd.Timestamp(d): float(v) for d, v in rows}).sort_index()
    return Panel("us_sofr", s.to_frame("SOFR"), "rate", 0, "nyfed_sofr", "USD")


# =============================================================================== Germany / euro area
def _bbk_wide_csv(path) -> pd.DataFrame:
    txt = path.read_bytes().decode("utf-8-sig")
    lines = txt.splitlines()
    sep = ";" if lines[0].count(";") > lines[0].count(",") else ","
    header = [h.strip('"') for h in lines[0].split(sep)]
    data_start = next(i for i, l in enumerate(lines) if re.match(r"^\d{4}-\d{2}-\d{2}" + sep, l))
    meta = lines[1:data_start]
    df = pd.read_csv(io.StringIO("\n".join(lines[data_start:])), sep=sep, header=None,
                     names=header, na_values=["."], dtype=str)
    df = df.rename(columns={header[0]: "date"})
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    keep = [c for c in df.columns if not c.endswith("_FLAGS")]
    dec = (lambda s: s.str.replace(",", ".")) if sep == ";" else (lambda s: s)
    df = df[keep].apply(lambda s: pd.to_numeric(dec(s), errors="coerce"))
    df.attrs["meta_lines"] = meta[:6]
    return df


def _bbk_maturity(key: str) -> float:
    code = key.split(".")[9]                 # e.g. R10XX, R005X, R015X
    m = re.match(r"R(\d{2})XX", code)
    if m:
        return float(m.group(1))
    m = re.match(r"R(\d{2})(\d)X", code)     # R005X = 0.5, R015X = 1.5
    if m:
        return float(m.group(1)) + float(m.group(2)) / 10.0
    raise ValueError(code)


def load_bundesbank() -> Panel:
    key = "D.I.ZST.ZI.EUR.S1311.B.A604..R.A.A._Z._Z.A"
    path = fetch("bbk", "svensson_zero_all.csv", f"https://api.statistiken.bundesbank.de/rest/data/BBSIS/{key}",
                 {"format": "csv", "lang": "en"}, max_age_days=0.5, timeout=180)
    df = _bbk_wide_csv(path)
    df.columns = [_bbk_maturity(c) for c in df.columns]
    df = df.sort_index(axis=1).dropna(how="all")
    return Panel("de_zero", df, "zero", -1, "bbk_svensson", "EUR",
                 {"compounding_note": "see docs/DATA.md (verified against Svensson formula)"})


def load_bundesbank_params() -> Panel:
    key = "D.I.ZST..EUR.S1311.B.A604._Z.R.A.A._Z._Z.A"
    path = fetch("bbk", "svensson_params.csv", f"https://api.statistiken.bundesbank.de/rest/data/BBSIS/{key}",
                 {"format": "csv", "lang": "en"}, max_age_days=0.5, timeout=180)
    df = _bbk_wide_csv(path)
    names = {"B0": "BETA0", "B1": "BETA1", "B2": "BETA2", "B3": "BETA3", "T1": "TAU1", "T2": "TAU2"}
    df.columns = [names[c.split(".")[4]] for c in df.columns]
    return Panel("de_params", df.dropna(how="all"), "params", 0, "bbk_svensson", "EUR")


def _ecb_series(key: str, name: str, max_age: float = 0.5) -> pd.Series:
    path = fetch("ecb", f"{name}.csv", f"https://data-api.ecb.europa.eu/service/data/{key}",
                 {"format": "csvdata"}, max_age_days=max_age, timeout=180)
    df = pd.read_csv(path, usecols=["TIME_PERIOD", "OBS_VALUE"])
    return pd.Series(df["OBS_VALUE"].to_numpy(float), index=pd.to_datetime(df["TIME_PERIOD"]), name=name)


def load_ecb_curve(rating: str = "A") -> Panel:
    """ECB Svensson parameters. rating 'A' = AAA-rated central government bonds,
    'C' = all euro area central government bonds."""
    cols = {}
    for p in ["BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2"]:
        cols[p] = _ecb_series(f"YC/B.U2.EUR.4F.G_N_{rating}.SV_C_YM.{p}", f"yc_{rating}_{p}")
    df = pd.DataFrame(cols).sort_index()
    return Panel(f"ea_{'aaa' if rating == 'A' else 'all'}_params", df, "params", 0, "ecb_yc", "EUR")


def load_ecb_spot(rating: str = "A", tenors=(1, 2, 3, 5, 7, 10, 15, 20, 30)) -> Panel:
    cols = {float(t): _ecb_series(f"YC/B.U2.EUR.4F.G_N_{rating}.SV_C_YM.SR_{t}Y", f"yc_{rating}_SR_{t}Y")
            for t in tenors}
    return Panel(f"ea_{'aaa' if rating == 'A' else 'all'}_spot", pd.DataFrame(cols).sort_index(),
                 "zero", 0, "ecb_yc", "EUR")


def load_estr() -> Panel:
    s = _ecb_series("EST/B.EU000A2X2A25.WT", "estr")
    return Panel("ea_estr", s.to_frame("ESTR"), "rate", 0, "ecb_estr", "EUR")


# =============================================================================== France
def load_france_tec() -> Panel:
    cols = {}
    for n in (1, 2, 3, 5, 7, 10, 15, 20, 25, 30):
        f = inbox_file(f"Webstat_Export_*FRMOYTEC{n}.HSTA*.csv")
        if f is None:
            continue
        lines = f.read_bytes().decode("utf-8-sig").splitlines()
        rows = []
        for l in lines:
            m = re.match(r"^(\d{4}-\d{2}-\d{2});(.*)$", l.strip())
            if m and m.group(2) not in ("-", ""):
                rows.append((m.group(1), float(m.group(2).replace(",", "."))))
        cols[float(n)] = pd.Series({pd.Timestamp(d): v for d, v in rows})
    if not cols:
        raise FileNotFoundError("no Banque de France TEC exports in data/inbox")
    df = pd.DataFrame(cols).sort_index().sort_index(axis=1)
    return Panel("fr_tec", df, "par", 1, "bdf_tec", "EUR",
                 {"tenors_available": sorted(cols)})


# =============================================================================== United Kingdom
def _boe_sheet(xbytes: bytes, sheet: str = "4. spot curve") -> pd.DataFrame:
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(xbytes), read_only=True, data_only=True)
    if sheet not in wb.sheetnames:
        # older archive files name the sheet differently ("4. nominal spot curve", ...)
        cands = [s for s in wb.sheetnames if "spot" in s.lower() and "short" not in s.lower()]
        if not cands:
            wb.close()
            return pd.DataFrame()
        sheet = cands[0]
    ws = wb[sheet]
    tenors, rows = None, []
    for r in ws.iter_rows(values_only=True):
        if r and isinstance(r[0], str) and r[0].strip().lower().startswith("years"):
            tenors = [float(x) if isinstance(x, (int, float)) else np.nan for x in r[1:]]
            continue
        if tenors is not None and r and isinstance(r[0], dt.datetime):
            vals = [float(x) if isinstance(x, (int, float)) else np.nan for x in r[1:len(tenors) + 1]]
            rows.append([pd.Timestamp(r[0])] + vals)
    wb.close()
    if tenors is None:
        return pd.DataFrame()
    df = pd.DataFrame(rows, columns=["date"] + tenors).set_index("date")
    df = df.loc[:, [c for c in df.columns if not (isinstance(c, float) and np.isnan(c))]]
    return df


def _boe_zip(pattern: str, sheet: str) -> pd.DataFrame:
    f = inbox_file(pattern)
    if f is None:
        return pd.DataFrame()
    zf = zipfile.ZipFile(f)
    frames = [_boe_sheet(zf.read(n), sheet) for n in sorted(zf.namelist()) if n.lower().endswith(".xlsx")]
    frames = [x for x in frames if len(x)]
    return pd.concat(frames) if frames else pd.DataFrame()


def load_uk(kind: str = "nominal") -> Panel:
    """BoE curves: kind in nominal | real | inflation | ois (spot, continuously compounded)."""
    arch = {"nominal": "glcnominalddata*.zip", "real": "glcrealddata*.zip",
            "inflation": "glcinflationddata*.zip", "ois": "oisddata*.zip"}[kind]
    latest_name = {"nominal": "GLC Nominal", "real": "GLC Real", "inflation": "GLC Inflation",
                   "ois": "OIS"}[kind]
    df = _boe_zip(arch, "4. spot curve")
    lf = inbox_file("latest-yield-curve-data*.zip")
    if lf is not None:
        zf = zipfile.ZipFile(lf)
        for n in zf.namelist():
            if n.startswith(latest_name + " daily"):
                cur = _boe_sheet(zf.read(n), "4. spot curve")
                df = pd.concat([df, cur]) if len(df) else cur
    if not len(df):
        raise FileNotFoundError(f"no Bank of England {kind} files in data/inbox")
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df = df.dropna(how="all").sort_index(axis=1)
    return Panel(f"uk_{kind}", df, "zero", 0, "boe_glc", "GBP")


# =============================================================================== Japan
def load_japan() -> Panel:
    base = "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/"
    hist = fetch("mof", "jgbcme_all.csv", base + "historical/jgbcme_all.csv", max_age_days=7)
    cur = fetch("mof", "jgbcme.csv", base + "jgbcme.csv", max_age_days=0.5)
    frames = []
    for p in (hist, cur):
        lines = p.read_bytes().decode("utf-8", errors="replace").splitlines()
        start = next(i for i, l in enumerate(lines) if l.startswith("Date,"))
        df = pd.read_csv(io.StringIO("\n".join(lines[start:])), na_values=["-", ""])
        df = df[df["Date"].astype(str).str.match(r"^\d{4}/\d{1,2}/\d{1,2}$")]
        df["Date"] = pd.to_datetime(df["Date"], format="%Y/%m/%d")
        frames.append(df.set_index("Date"))
    df = pd.concat(frames)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df.columns = [float(c.rstrip("Y")) for c in df.columns]
    df = df.apply(pd.to_numeric, errors="coerce")
    return Panel("jp_par", df, "par", 2, "mof_jgb", "JPY")


# =============================================================================== FRED files (inbox)
def load_fred_swaps() -> Panel:
    f = inbox_file("fred_swaps*.csv")
    if f is None:
        raise FileNotFoundError("fred_swaps.csv not in data/inbox")
    df = pd.read_csv(f, parse_dates=["observation_date"], index_col="observation_date")
    df = df.apply(pd.to_numeric, errors="coerce").dropna(how="all")
    df.columns = [float(c.replace("DSWP", "")) for c in df.columns]
    return Panel("us_swaps_ice", df, "par", 2, "fred_swaps", "USD",
                 {"note": "USD swap rates vs 3m LIBOR, semiannual 30/360 fixed leg (ICE), 2000-2016"})


def load_fred_moodys() -> Panel:
    f = inbox_file("fred_moodys*.csv")
    if f is None:
        raise FileNotFoundError("fred_moodys.csv not in data/inbox")
    df = pd.read_csv(f, parse_dates=["observation_date"], index_col="observation_date")
    df = df.apply(pd.to_numeric, errors="coerce").dropna(how="all")
    return Panel("us_moodys", df, "ytm", 2, "fred_moodys", "USD")


# =============================================================================== BIS / OECD
BIS_AREAS = {"US": "US", "XM": "EA", "GB": "UK", "JP": "JP", "PL": "PL"}


def load_policy_rates() -> Panel:
    cols = {}
    for code, label in BIS_AREAS.items():
        path = fetch("bis", f"cbpol_{code}.csv", f"https://stats.bis.org/api/v1/data/WS_CBPOL/D.{code}/all",
                     {"format": "csv", "startPeriod": "1990-01-01"}, max_age_days=1)
        df = pd.read_csv(path, usecols=["TIME_PERIOD", "OBS_VALUE"])
        cols[label] = pd.Series(df["OBS_VALUE"].to_numpy(float), index=pd.to_datetime(df["TIME_PERIOD"]))
    out = pd.DataFrame(cols).sort_index()
    return Panel("policy_rates", out, "rate", 0, "bis_policy", "")


OECD_COUNTRIES = {"USA": "US", "DEU": "DE", "FRA": "FR", "POL": "PL", "GBR": "UK", "JPN": "JP"}


def load_oecd_rates() -> Panel:
    """Monthly 3-month interbank (IR3TIB) and long-term government (IRLT) rates."""
    areas = "+".join(OECD_COUNTRIES)
    url = (f"https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_FINMARK,4.0/"
           f"{areas}.M.IR3TIB+IRLT.PA.....")
    path = fetch("oecd", "finmark.csv", url, {"startPeriod": "1990-01", "format": "csvfile"},
                 max_age_days=7, timeout=180)
    df = pd.read_csv(path)
    df = df[["REF_AREA", "MEASURE", "TIME_PERIOD", "OBS_VALUE"]]
    df["col"] = df["REF_AREA"].map(OECD_COUNTRIES) + "_" + df["MEASURE"].map({"IR3TIB": "3m", "IRLT": "10y"})
    wide = df.pivot_table(index="TIME_PERIOD", columns="col", values="OBS_VALUE")
    wide.index = pd.PeriodIndex(wide.index, freq="M").to_timestamp(how="end").normalize()
    return Panel("oecd_rates", wide.sort_index(), "rate", 0, "oecd_mei", "")


def load_oecd_fiscal() -> Panel:
    """General government gross debt (GGFLQ), Maastricht debt (GGFLMQ) and net lending
    (NLGQ), % of GDP, annual, OECD Economic Outlook (latest years are projections)."""
    areas = "+".join(OECD_COUNTRIES)
    url = (f"https://sdmx.oecd.org/public/rest/data/OECD.ECO.MAD,DSD_EO@DF_EO,1.5/"
           f"{areas}.GGFLQ+NLGQ+GGFLMQ.A")
    path = fetch("oecd", "eo_fiscal.csv", url, {"startPeriod": "1995", "format": "csvfile"},
                 max_age_days=7, timeout=180)
    df = pd.read_csv(path)[["REF_AREA", "MEASURE", "TIME_PERIOD", "OBS_VALUE"]]
    df["col"] = df["REF_AREA"].map(OECD_COUNTRIES) + "_" + df["MEASURE"]
    wide = df.pivot_table(index="TIME_PERIOD", columns="col", values="OBS_VALUE")
    wide.index = pd.to_datetime(wide.index.astype(str) + "-12-31")
    return Panel("oecd_fiscal", wide.sort_index(), "rate", 0, "oecd_eo", "",
                 {"note": "OECD Economic Outlook; years after the latest outturn are OECD projections"})


def load_fx() -> Panel:
    """ECB euro reference rates: units of each currency per 1 EUR."""
    cols = {}
    for ccy in ("PLN", "USD", "GBP", "JPY"):
        cols[ccy] = _ecb_series(f"EXR/D.{ccy}.EUR.SP00.A", f"exr_{ccy}")
    return Panel("fx_eur", pd.DataFrame(cols).sort_index(), "rate", 0, "ecb_fx", "")


def load_cpi() -> Panel:
    """Consumer prices, year-on-year change (%), monthly - BIS long series of national CPIs
    (WS_LONG_CPI, unit 771). Used instead of the OECD prices dataflow, whose French, Polish
    and Japanese series stopped updating (Dec 2025 / Jun 2021) when checked in Nov 2026."""
    path = fetch("bis", "long_cpi.csv", "https://stats.bis.org/api/v1/data/WS_LONG_CPI/M.US+DE+FR+PL+GB+JP.771/all",
                 {"format": "csv", "startPeriod": "1990-01"}, max_age_days=7)
    df = pd.read_csv(path, usecols=["REF_AREA", "TIME_PERIOD", "OBS_VALUE"])
    wide = df.pivot_table(index="TIME_PERIOD", columns="REF_AREA", values="OBS_VALUE")
    wide = wide.rename(columns={"GB": "UK"})
    wide.index = pd.PeriodIndex(wide.index, freq="M").to_timestamp(how="end").normalize()
    return Panel("cpi_yoy", wide.sort_index(), "rate", 0, "bis_cpi", "")
