# France vs Poland: generated tables

Weekly data to 2026-11-20.

| measure | now_bp | 1y_ago_bp | 5y_mean_bp | 5y_min_bp | 5y_max_bp |
|---|---:|---:|---:|---:|---:|
| PL-FR 2y | 100.6 | 189.5 | 281.8 | 100.6 | 709.6 |
| PL-FR 5y | 143.8 | 200.3 | 289.4 | 139.1 | 632.9 |
| PL-FR 10y | 136.2 | 184.2 | 271.4 | 130.0 | 570.2 |
| PL 2s10s | 159.5 | 119.7 | 56.5 | -101.1 | 164.2 |
| FR 2s10s | 123.8 | 125.0 | 66.9 | -30.0 | 145.0 |
| slope gap (PL-FR 2s10s) | 35.7 | -5.3 | -10.4 | -201.6 | 88.7 |

## Co-movement (52-week windows, latest)

| date | beta_PL_on_FR | corr | vol_PL10_bp | vol_FR10_bp |
|---|---:|---:|---:|---:|
| 2026-11-20 | 0.957 | 0.651 | 112.260 | 76.344 |

## FX-hedged comparison (PLN hedged into EUR via short-rate differential)

| date | r_PLN | r_EUR | hedge_cost | PL10_hedged_EUR | FR10 | hedged_pickup_bp |
|---|---:|---:|---:|---:|---:|---:|
| 2026-11-20 | 3.750 | 2.441 | 1.309 | 4.927 | 4.874 | 5.307 |

## Candidate trades

| trade | signal | test | start | end | ann_return_bp | ann_vol_bp | sharpe | t_nw | max_dd_bp | cost_bp_per_year | params |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| PL 10y vs FR 10y, DV01-neutral (long PL) | static | full sample | 2006-01-06 | 2026-11-20 | -20.54 | 104.02 | -0.20 | -0.99 | -859.78 | 19.37 |  |
| PL 10y vs FR 10y, DV01-neutral (long PL) | meanrev | full sample | 2006-01-06 | 2026-11-20 | -2.38 | 87.92 | -0.03 | -0.14 | -511.92 | 19.60 |  |
| PL 10y vs FR 10y, DV01-neutral (long PL) | meanrev | out-of-sample (second half) | 2016-05-06 | 2026-11-20 | -2.41 | 73.54 | -0.03 | -0.11 | -414.44 | 18.13 | {'lookback': 26, 'entry': 2.0, 'exit': 0.5} |
| PL 10y vs FR 10y, DV01-neutral (long PL) | meanrev | walk-forward OOS | 2010-01-08 | 2026-11-20 | 9.68 | 72.97 | 0.13 | 0.56 | -414.44 | 19.18 |  |
| PL 10y vs FR 10y, DV01-neutral (long PL) | carry | full sample | 2006-01-06 | 2026-11-20 | -14.81 | 103.76 | -0.14 | -0.70 | -454.72 | 32.75 |  |
| PL 5y vs FR 5y, DV01-neutral (long PL) | static | full sample | 2006-01-06 | 2026-11-20 | -16.63 | 112.67 | -0.15 | -0.71 | -870.26 | 23.20 |  |
| PL 5y vs FR 5y, DV01-neutral (long PL) | meanrev | full sample | 2006-01-06 | 2026-11-20 | -5.74 | 89.97 | -0.06 | -0.31 | -711.36 | 20.15 |  |
| PL 5y vs FR 5y, DV01-neutral (long PL) | meanrev | out-of-sample (second half) | 2016-06-24 | 2026-11-20 | -30.72 | 97.86 | -0.31 | -1.04 | -534.77 | 13.93 | {'lookback': 104, 'entry': 2.0, 'exit': 0.5} |
| PL 5y vs FR 5y, DV01-neutral (long PL) | meanrev | walk-forward OOS | 2010-01-08 | 2026-11-20 | -19.17 | 87.14 | -0.22 | -0.93 | -637.36 | 15.65 |  |
| PL 5y vs FR 5y, DV01-neutral (long PL) | carry | full sample | 2006-01-06 | 2026-11-20 | -19.81 | 111.19 | -0.18 | -0.87 | -731.02 | 42.10 |  |
| PL 2y vs FR 2y, DV01-neutral (long PL) | static | full sample | 2006-01-06 | 2026-11-20 | -14.00 | 112.50 | -0.12 | -0.57 | -970.17 | 39.21 |  |
| PL 2y vs FR 2y, DV01-neutral (long PL) | meanrev | full sample | 2006-01-06 | 2026-11-20 | -65.11 | 93.96 | -0.69 | -3.29 | -1,358.94 | 37.80 |  |
| PL 2y vs FR 2y, DV01-neutral (long PL) | meanrev | out-of-sample (second half) | 2016-06-24 | 2026-11-20 | -70.88 | 94.02 | -0.75 | -2.46 | -799.62 | 24.96 | {'lookback': 52, 'entry': 2.0, 'exit': 0.5} |
| PL 2y vs FR 2y, DV01-neutral (long PL) | meanrev | walk-forward OOS | 2010-01-08 | 2026-11-20 | -43.43 | 90.75 | -0.48 | -1.92 | -992.09 | 25.28 |  |
| PL 2y vs FR 2y, DV01-neutral (long PL) | carry | full sample | 2006-01-06 | 2026-11-20 | -39.39 | 110.33 | -0.36 | -1.63 | -1,193.52 | 67.85 |  |
| Curve box: PL 2s10s steepener vs FR 2s10s flattener | static | full sample | 2006-01-06 | 2026-11-20 | -31.75 | 84.76 | -0.37 | -1.78 | -782.42 | 58.11 |  |
| Curve box: PL 2s10s steepener vs FR 2s10s flattener | meanrev | full sample | 2006-01-06 | 2026-11-20 | -60.03 | 70.11 | -0.86 | -4.09 | -1,262.91 | 59.87 |  |
| Curve box: PL 2s10s steepener vs FR 2s10s flattener | meanrev | out-of-sample (second half) | 2016-05-06 | 2026-11-20 | -13.84 | 58.68 | -0.24 | -0.79 | -258.45 | 25.80 | {'lookback': 104, 'entry': 2.0, 'exit': 0.5} |
| Curve box: PL 2s10s steepener vs FR 2s10s flattener | meanrev | walk-forward OOS | 2010-01-08 | 2026-11-20 | -24.59 | 60.22 | -0.41 | -1.76 | -559.48 | 32.25 |  |
| Curve box: PL 2s10s steepener vs FR 2s10s flattener | carry | full sample | 2006-01-06 | 2026-11-20 | -69.63 | 85.54 | -0.81 | -3.89 | -1,470.89 | 116.57 |  |
| PL 2s10s steepener | static | full sample | 2006-01-06 | 2026-11-20 | -34.40 | 73.76 | -0.47 | -2.22 | -858.22 | 51.39 |  |
| PL 2s10s steepener | meanrev | full sample | 2006-01-06 | 2026-11-20 | -54.10 | 60.22 | -0.90 | -4.29 | -1,129.54 | 45.16 |  |
| PL 2s10s steepener | meanrev | out-of-sample (second half) | 2016-05-06 | 2026-11-20 | -32.46 | 68.37 | -0.47 | -1.64 | -404.14 | 41.93 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| PL 2s10s steepener | meanrev | walk-forward OOS | 2010-01-08 | 2026-11-20 | -32.12 | 61.91 | -0.52 | -2.27 | -562.55 | 38.54 |  |
| PL 2s10s steepener | carry | full sample | 2006-01-06 | 2026-11-20 | -83.66 | 77.28 | -1.08 | -4.88 | -1,778.84 | 94.99 |  |
| FR 2s10s steepener | static | full sample | 2004-11-03 | 2026-11-20 | -19.98 | 56.05 | -0.36 | -1.76 | -618.57 | 6.82 |  |
| FR 2s10s steepener | meanrev | full sample | 2004-11-03 | 2026-11-20 | -20.20 | 45.54 | -0.44 | -2.20 | -489.30 | 6.63 |  |
| FR 2s10s steepener | meanrev | out-of-sample (second half) | 2015-11-12 | 2026-11-20 | -24.13 | 49.78 | -0.48 | -1.94 | -357.05 | 6.40 | {'lookback': 104, 'entry': 1.0, 'exit': 0.0} |
| FR 2s10s steepener | meanrev | walk-forward OOS | 2008-01-02 | 2026-11-20 | -20.09 | 53.41 | -0.38 | -1.76 | -451.23 | 6.93 |  |
| FR 2s10s steepener | carry | full sample | 2004-11-03 | 2026-11-20 | 24.97 | 56.00 | 0.45 | 2.23 | -141.31 | 10.76 |  |

## Macro and fiscal (OECD; policy rates from BIS)

| year | cpi_avg_FR | debt_FR | maastricht_debt_FR | balance_FR | cpi_avg_PL | debt_PL | maastricht_debt_PL | balance_PL | policy_end_ECB | policy_end_NBP |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2,015.00 | 0.04 | 121.48 | 96.92 | -3.89 | -0.91 | 70.11 | 51.14 | -2.60 | 0.05 | 1.50 |
| 2,016.00 | 0.18 | 124.99 | 98.21 | -3.77 | -0.65 | 72.95 | 54.10 | -2.38 | 0.00 | 1.50 |
| 2,017.00 | 1.03 | 124.79 | 98.64 | -3.36 | 2.00 | 68.61 | 50.45 | -1.49 | 0.00 | 1.50 |
| 2,018.00 | 1.85 | 122.72 | 98.46 | -2.32 | 1.80 | 66.18 | 48.27 | -0.25 | 0.00 | 1.50 |
| 2,019.00 | 1.11 | 122.72 | 98.03 | -2.39 | 2.18 | 63.25 | 45.26 | -0.73 | 0.00 | 1.50 |
| 2,020.00 | 0.48 | 144.67 | 114.96 | -8.94 | 3.37 | 76.92 | 56.63 | -6.86 | 0.00 | 0.10 |
| 2,021.00 | 1.64 | 136.85 | 112.93 | -6.59 | 5.15 | 67.39 | 53.03 | -1.68 | 0.00 | 1.75 |
| 2,022.00 | 5.22 | 115.50 | 111.42 | -4.75 | 14.37 | 58.81 | 48.87 | -3.37 | 2.50 | 6.75 |
| 2,023.00 | 4.89 | 116.25 | 109.65 | -5.37 | 11.61 | 62.11 | 49.58 | -5.20 | 4.50 | 5.75 |
| 2,024.00 | 2.00 | 115.56 | 113.17 | -5.79 | 3.80 | 67.18 | 55.00 | -6.47 | 3.00 | 5.75 |
| 2,025.00 | 0.94 | 116.75 | 115.96 | -5.11 | 3.87 | 73.14 | 59.78 | -7.27 | 2.00 | 4.00 |
| 2,026.00 | 1.86 | 119.57 | 118.77 | -4.96 | 2.90 | 77.37 | 64.01 | -6.87 | 2.50 | 3.75 |
| 2,027.00 |  | 121.67 | 120.87 | -4.58 |  | 81.06 | 67.71 | -6.28 |  |  |
