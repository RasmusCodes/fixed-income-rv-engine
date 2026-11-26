# Files to download by hand (save them in data/inbox)

These official sources refuse requests from scripts (HTTP 403 or bot challenges), so they are downloaded in a normal browser. Every other source is fetched by `scripts/fetch_data.py`.
Save each file into `data/inbox/` (create it) with its default name. The Banque de France export is a semicolon-separated CSV named `Webstat_Export_fr_<series code>.csv`.

## 1. Bank of England yield curves (5 zip files)

Page: https://www.bankofengland.co.uk/statistics/yield-curves

- https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/latest-yield-curve-data.zip (0.4 MB)
- https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/glcnominalddata.zip (39.3 MB)
- https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/glcrealddata.zip (25.2 MB)
- https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/glcinflationddata.zip (24.9 MB)
- https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/oisddata.zip (11.8 MB)

## 2. Banque de France: French constant-maturity OAT yields (TEC), 10 series

On each page, click **Télécharger les données** and choose CSV (all dates).

- https://webstat.banque-france.fr/fr/catalogue/fm/FM.D.FR.EUR.FR2.BB.FRMOYTEC1.HSTA
- https://webstat.banque-france.fr/fr/catalogue/fm/FM.D.FR.EUR.FR2.BB.FRMOYTEC2.HSTA
- https://webstat.banque-france.fr/fr/catalogue/fm/FM.D.FR.EUR.FR2.BB.FRMOYTEC3.HSTA
- https://webstat.banque-france.fr/fr/catalogue/fm/FM.D.FR.EUR.FR2.BB.FRMOYTEC5.HSTA
- https://webstat.banque-france.fr/fr/catalogue/fm/FM.D.FR.EUR.FR2.BB.FRMOYTEC7.HSTA
- https://webstat.banque-france.fr/fr/catalogue/fm/FM.D.FR.EUR.FR2.BB.FRMOYTEC10.HSTA
- https://webstat.banque-france.fr/fr/catalogue/fm/FM.D.FR.EUR.FR2.BB.FRMOYTEC15.HSTA
- https://webstat.banque-france.fr/fr/catalogue/fm/FM.D.FR.EUR.FR2.BB.FRMOYTEC20.HSTA
- https://webstat.banque-france.fr/fr/catalogue/fm/FM.D.FR.EUR.FR2.BB.FRMOYTEC25.HSTA
- https://webstat.banque-france.fr/fr/catalogue/fm/FM.D.FR.EUR.FR2.BB.FRMOYTEC30.HSTA

## 3. FRED (2 CSV files; rename them `fred_swaps.csv` and `fred_moodys.csv`)

- ICE USD swap rates 2000-2016 (discontinued series):
  https://fred.stlouisfed.org/graph/fredgraph.csv?id=DSWP1,DSWP2,DSWP3,DSWP4,DSWP5,DSWP7,DSWP10,DSWP30
- Moody's seasoned Aaa and Baa corporate yields:
  https://fred.stlouisfed.org/graph/fredgraph.csv?id=DAAA,DBAA

The loaders in `firv/data/loaders.py` find these files in `data/inbox/` by name pattern; nothing else is needed.
They are required for the French and UK curves, the swap-spread and UK breakeven studies and the Moody's credit
spread; the US, German, Japanese, Polish and euro-area work needs none of them.
