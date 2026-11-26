# Strategy backtests: generated tables

P&L in bp per unit of DV01 per year (1 unit = the trade's DV01 per bp). Costs at 1x the assumptions unless stated.

## Full sample, fixed default parameters

| family | strategy | signal | test | start | end | ann_return_bp | ann_vol_bp | sharpe | t_nw | max_dd_bp | cost_bp_per_year | turnover_per_year |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| curve | US 2s10s steepener | static | full sample, costs x1 | 1990-01-02 | 2026-11-20 | 16.99 | 58.81 | 0.29 | 1.83 | -376.19 | 3.60 | 0.03 |
| curve | US 2s10s steepener | meanrev | full sample, costs x1 | 1990-01-02 | 2026-11-20 | -24.16 | 51.52 | -0.47 | -2.99 | -1,045.61 | 3.40 | 1.82 |
| curve | US 2s10s steepener | carry | full sample, costs x1 | 1990-01-02 | 2026-11-20 | 6.95 | 58.87 | 0.12 | 0.75 | -475.28 | 5.94 | 5.23 |
| curve | US 2s10s steepener | momentum | full sample, costs x1 | 1990-01-02 | 2026-11-20 | 3.02 | 58.69 | 0.05 | 0.32 | -337.16 | 8.82 | 11.79 |
| curve | US 5s30s steepener | static | full sample, costs x1 | 1993-10-01 | 2026-11-20 | 14.33 | 60.35 | 0.24 | 1.41 | -219.47 | 4.61 | 0.00 |
| curve | US 5s30s steepener | meanrev | full sample, costs x1 | 1993-10-01 | 2026-11-20 | -1.27 | 44.40 | -0.03 | -0.17 | -329.05 | 4.45 | 2.26 |
| curve | US 5s30s steepener | carry | full sample, costs x1 | 1993-10-01 | 2026-11-20 | 7.92 | 60.41 | 0.13 | 0.77 | -329.17 | 6.10 | 2.29 |
| curve | US 5s30s steepener | momentum | full sample, costs x1 | 1993-10-01 | 2026-11-20 | -5.15 | 60.54 | -0.09 | -0.50 | -432.83 | 12.14 | 11.62 |
| butterfly | US 2s5s10s fly 50/50 (long belly) | static | full sample, costs x1 | 1990-01-02 | 2026-11-20 | -2.14 | 24.29 | -0.09 | -0.64 | -187.43 | 3.80 | 0.03 |
| butterfly | US 2s5s10s fly 50/50 (long belly) | meanrev | full sample, costs x1 | 1990-01-02 | 2026-11-20 | 0.83 | 18.95 | 0.04 | 0.32 | -55.91 | 3.77 | 3.06 |
| butterfly | US 2s5s10s fly 50/50 (long belly) | carry | full sample, costs x1 | 1990-01-02 | 2026-11-20 | 5.31 | 24.45 | 0.22 | 1.55 | -113.40 | 8.28 | 9.46 |
| butterfly | US 2s5s10s fly 50/50 (long belly) | momentum | full sample, costs x1 | 1990-01-02 | 2026-11-20 | -17.09 | 24.43 | -0.70 | -4.84 | -670.47 | 11.91 | 17.22 |
| butterfly | US 2s5s10s fly PCA-weighted (long belly) | static | full sample, costs x1 | 1990-01-02 | 2026-11-20 | -6.61 | 22.24 | -0.30 | -2.34 | -302.69 | 4.20 | 0.03 |
| butterfly | US 2s5s10s fly PCA-weighted (long belly) | meanrev | full sample, costs x1 | 1990-01-02 | 2026-11-20 | 0.04 | 17.47 | 0.00 | 0.02 | -97.44 | 4.39 | 3.52 |
| butterfly | US 2s5s10s fly PCA-weighted (long belly) | carry | full sample, costs x1 | 1990-01-02 | 2026-11-20 | 3.74 | 22.41 | 0.17 | 1.26 | -148.62 | 8.55 | 8.49 |
| butterfly | US 2s5s10s fly PCA-weighted (long belly) | momentum | full sample, costs x1 | 1990-01-02 | 2026-11-20 | -18.53 | 22.43 | -0.83 | -5.83 | -706.20 | 12.21 | 15.70 |
| curve | DE 2s10s steepener | static | full sample, costs x1 | 1997-08-07 | 2026-11-20 | -17.95 | 56.07 | -0.32 | -1.93 | -649.85 | 5.22 | 0.03 |
| curve | DE 2s10s steepener | meanrev | full sample, costs x1 | 1997-08-07 | 2026-11-20 | -17.78 | 46.38 | -0.38 | -2.34 | -554.43 | 4.73 | 2.08 |
| curve | DE 2s10s steepener | carry | full sample, costs x1 | 1997-08-07 | 2026-11-20 | -2.34 | 56.04 | -0.04 | -0.25 | -386.89 | 8.32 | 4.81 |
| curve | DE 2s10s steepener | momentum | full sample, costs x1 | 1997-08-07 | 2026-11-20 | 7.55 | 55.90 | 0.14 | 0.82 | -201.88 | 12.45 | 11.23 |
| curve | DE 5s30s steepener | static | full sample, costs x1 | 2000-08-01 | 2026-11-20 | 2.55 | 57.16 | 0.04 | 0.26 | -305.82 | 6.42 | 0.04 |
| curve | DE 5s30s steepener | meanrev | full sample, costs x1 | 2000-08-01 | 2026-11-20 | -9.32 | 46.80 | -0.20 | -1.12 | -297.97 | 5.87 | 1.94 |
| curve | DE 5s30s steepener | carry | full sample, costs x1 | 2000-08-01 | 2026-11-20 | 1.60 | 57.11 | 0.03 | 0.16 | -202.75 | 9.95 | 4.45 |
| curve | DE 5s30s steepener | momentum | full sample, costs x1 | 2000-08-01 | 2026-11-20 | -10.31 | 57.13 | -0.18 | -1.03 | -460.36 | 17.49 | 13.95 |
| butterfly | DE 2s5s10s fly 50/50 (long belly) | static | full sample, costs x1 | 1997-08-07 | 2026-11-20 | -0.18 | 22.66 | -0.01 | -0.06 | -54.01 | 5.02 | 0.03 |
| butterfly | DE 2s5s10s fly 50/50 (long belly) | meanrev | full sample, costs x1 | 1997-08-07 | 2026-11-20 | -1.85 | 18.27 | -0.10 | -0.78 | -86.12 | 5.23 | 3.59 |
| butterfly | DE 2s5s10s fly 50/50 (long belly) | carry | full sample, costs x1 | 1997-08-07 | 2026-11-20 | -4.95 | 22.76 | -0.22 | -1.61 | -159.35 | 8.30 | 5.29 |
| butterfly | DE 2s5s10s fly 50/50 (long belly) | momentum | full sample, costs x1 | 1997-08-07 | 2026-11-20 | -22.51 | 22.98 | -0.98 | -6.71 | -664.21 | 16.15 | 17.93 |
| butterfly | DE 2s5s10s fly PCA-weighted (long belly) | static | full sample, costs x1 | 1997-08-07 | 2026-11-20 | -4.74 | 21.71 | -0.22 | -1.74 | -183.61 | 5.58 | 0.03 |
| butterfly | DE 2s5s10s fly PCA-weighted (long belly) | meanrev | full sample, costs x1 | 1997-08-07 | 2026-11-20 | -5.24 | 17.35 | -0.30 | -2.24 | -196.20 | 5.71 | 3.28 |
| butterfly | DE 2s5s10s fly PCA-weighted (long belly) | carry | full sample, costs x1 | 1997-08-07 | 2026-11-20 | -10.43 | 21.78 | -0.48 | -3.77 | -326.28 | 10.25 | 6.93 |
| butterfly | DE 2s5s10s fly PCA-weighted (long belly) | momentum | full sample, costs x1 | 1997-08-07 | 2026-11-20 | -21.00 | 22.08 | -0.95 | -6.49 | -622.31 | 16.77 | 16.70 |
| curve | FR 2s10s steepener | static | full sample, costs x1 | 2004-11-03 | 2026-11-20 | -19.98 | 56.05 | -0.36 | -1.76 | -618.57 | 6.82 | 0.05 |
| curve | FR 2s10s steepener | meanrev | full sample, costs x1 | 2004-11-03 | 2026-11-20 | -20.20 | 45.54 | -0.44 | -2.20 | -489.30 | 6.63 | 2.27 |
| curve | FR 2s10s steepener | carry | full sample, costs x1 | 2004-11-03 | 2026-11-20 | 24.97 | 56.00 | 0.45 | 2.23 | -141.31 | 10.76 | 4.67 |
| curve | FR 2s10s steepener | momentum | full sample, costs x1 | 2004-11-03 | 2026-11-20 | 11.22 | 56.22 | 0.20 | 1.01 | -301.89 | 15.00 | 9.75 |
| curve | FR 5s30s steepener | static | full sample, costs x1 | 2006-10-02 | 2026-11-20 | 6.48 | 58.18 | 0.11 | 0.55 | -267.45 | 8.80 | 0.05 |
| curve | FR 5s30s steepener | meanrev | full sample, costs x1 | 2006-10-02 | 2026-11-20 | -8.06 | 48.40 | -0.17 | -0.81 | -263.14 | 8.80 | 2.63 |
| curve | FR 5s30s steepener | carry | full sample, costs x1 | 2006-10-02 | 2026-11-20 | 5.42 | 58.16 | 0.09 | 0.46 | -263.94 | 13.39 | 4.22 |
| curve | FR 5s30s steepener | momentum | full sample, costs x1 | 2006-10-02 | 2026-11-20 | -15.89 | 58.69 | -0.27 | -1.29 | -457.29 | 24.20 | 14.16 |
| butterfly | FR 2s5s10s fly 50/50 (long belly) | static | full sample, costs x1 | 2004-11-03 | 2026-11-20 | -0.31 | 28.88 | -0.01 | -0.08 | -73.80 | 6.62 | 0.05 |
| butterfly | FR 2s5s10s fly 50/50 (long belly) | meanrev | full sample, costs x1 | 2004-11-03 | 2026-11-20 | 0.19 | 23.19 | 0.01 | 0.06 | -74.24 | 6.77 | 3.49 |
| butterfly | FR 2s5s10s fly 50/50 (long belly) | carry | full sample, costs x1 | 2004-11-03 | 2026-11-20 | 3.68 | 29.02 | 0.13 | 0.88 | -53.82 | 12.39 | 7.03 |
| butterfly | FR 2s5s10s fly 50/50 (long belly) | momentum | full sample, costs x1 | 2004-11-03 | 2026-11-20 | -26.50 | 28.43 | -0.93 | -5.89 | -599.46 | 19.87 | 16.28 |
| butterfly | FR 2s5s10s fly PCA-weighted (long belly) | static | full sample, costs x1 | 2004-11-03 | 2026-11-20 | -8.76 | 30.46 | -0.29 | -1.99 | -233.89 | 7.74 | 0.05 |
| butterfly | FR 2s5s10s fly PCA-weighted (long belly) | meanrev | full sample, costs x1 | 2004-11-03 | 2026-11-20 | -1.16 | 24.29 | -0.05 | -0.31 | -115.57 | 7.78 | 3.54 |
| butterfly | FR 2s5s10s fly PCA-weighted (long belly) | carry | full sample, costs x1 | 2004-11-03 | 2026-11-20 | -1.78 | 30.72 | -0.06 | -0.38 | -142.71 | 19.08 | 12.11 |
| butterfly | FR 2s5s10s fly PCA-weighted (long belly) | momentum | full sample, costs x1 | 2004-11-03 | 2026-11-20 | -31.51 | 31.09 | -1.01 | -6.42 | -696.83 | 23.73 | 18.19 |
| curve | UK 2s10s steepener | static | full sample, costs x1 | 1990-01-02 | 2026-11-19 | -6.60 | 60.30 | -0.11 | -0.62 | -651.03 | 5.60 | 0.03 |
| curve | UK 2s10s steepener | meanrev | full sample, costs x1 | 1990-01-02 | 2026-11-19 | -13.41 | 54.61 | -0.25 | -1.48 | -751.47 | 5.68 | 2.09 |
| curve | UK 2s10s steepener | carry | full sample, costs x1 | 1990-01-02 | 2026-11-19 | 9.58 | 60.40 | 0.16 | 0.96 | -274.39 | 9.74 | 5.94 |
| curve | UK 2s10s steepener | momentum | full sample, costs x1 | 1990-01-02 | 2026-11-19 | -11.02 | 60.36 | -0.18 | -1.07 | -507.11 | 14.18 | 12.34 |
| curve | UK 5s30s steepener | static | full sample, costs x1 | 2016-01-04 | 2026-11-19 | -20.72 | 53.82 | -0.39 | -1.30 | -286.58 | 7.20 | 0.09 |
| curve | UK 5s30s steepener | meanrev | full sample, costs x1 | 2016-01-04 | 2026-11-19 | 4.31 | 44.78 | 0.10 | 0.34 | -102.38 | 6.70 | 2.30 |
| curve | UK 5s30s steepener | carry | full sample, costs x1 | 2016-01-04 | 2026-11-19 | -22.21 | 53.92 | -0.41 | -1.38 | -272.85 | 11.17 | 4.51 |
| curve | UK 5s30s steepener | momentum | full sample, costs x1 | 2016-01-04 | 2026-11-19 | -22.91 | 54.11 | -0.42 | -1.40 | -322.32 | 20.77 | 15.36 |
| butterfly | UK 2s5s10s fly 50/50 (long belly) | static | full sample, costs x1 | 1990-01-02 | 2026-11-19 | -0.84 | 15.04 | -0.06 | -0.32 | -133.22 | 5.20 | 0.03 |
| butterfly | UK 2s5s10s fly 50/50 (long belly) | meanrev | full sample, costs x1 | 1990-01-02 | 2026-11-19 | -6.83 | 12.18 | -0.56 | -3.23 | -293.11 | 4.92 | 2.52 |
| butterfly | UK 2s5s10s fly 50/50 (long belly) | carry | full sample, costs x1 | 1990-01-02 | 2026-11-19 | 4.11 | 15.18 | 0.27 | 1.56 | -58.27 | 8.05 | 4.42 |
| butterfly | UK 2s5s10s fly 50/50 (long belly) | momentum | full sample, costs x1 | 1990-01-02 | 2026-11-19 | -12.40 | 15.40 | -0.81 | -4.54 | -478.43 | 13.27 | 12.50 |
| butterfly | UK 2s5s10s fly PCA-weighted (long belly) | static | full sample, costs x1 | 1990-01-02 | 2026-11-19 | -3.55 | 13.46 | -0.26 | -1.52 | -200.72 | 5.54 | 0.03 |
| butterfly | UK 2s5s10s fly PCA-weighted (long belly) | meanrev | full sample, costs x1 | 1990-01-02 | 2026-11-19 | -4.77 | 10.94 | -0.44 | -2.54 | -200.08 | 5.29 | 2.47 |
| butterfly | UK 2s5s10s fly PCA-weighted (long belly) | carry | full sample, costs x1 | 1990-01-02 | 2026-11-19 | 0.82 | 13.65 | 0.06 | 0.35 | -84.90 | 8.74 | 4.75 |
| butterfly | UK 2s5s10s fly PCA-weighted (long belly) | momentum | full sample, costs x1 | 1990-01-02 | 2026-11-19 | -16.46 | 14.00 | -1.18 | -6.47 | -619.12 | 14.24 | 12.83 |
| curve | JP 2s10s steepener | static | full sample, costs x1 | 1990-01-04 | 2026-11-19 | -4.78 | 37.56 | -0.13 | -0.74 | -697.14 | 8.00 | 0.03 |
| curve | JP 2s10s steepener | meanrev | full sample, costs x1 | 1990-01-04 | 2026-11-19 | -10.69 | 29.37 | -0.36 | -2.08 | -467.66 | 7.32 | 2.44 |
| curve | JP 2s10s steepener | carry | full sample, costs x1 | 1990-01-04 | 2026-11-19 | 13.16 | 37.68 | 0.35 | 2.06 | -136.67 | 14.62 | 6.64 |
| curve | JP 2s10s steepener | momentum | full sample, costs x1 | 1990-01-04 | 2026-11-19 | -20.47 | 37.57 | -0.54 | -3.09 | -924.65 | 21.29 | 13.37 |
| curve | JP 5s30s steepener | static | full sample, costs x1 | 1999-09-02 | 2026-11-19 | -5.81 | 35.44 | -0.16 | -0.85 | -282.19 | 10.46 | 0.04 |
| curve | JP 5s30s steepener | meanrev | full sample, costs x1 | 1999-09-02 | 2026-11-19 | -9.37 | 28.31 | -0.33 | -1.67 | -327.82 | 9.84 | 2.50 |
| curve | JP 5s30s steepener | carry | full sample, costs x1 | 1999-09-02 | 2026-11-19 | 1.49 | 35.48 | 0.04 | 0.21 | -175.15 | 14.47 | 3.12 |
| curve | JP 5s30s steepener | momentum | full sample, costs x1 | 1999-09-02 | 2026-11-19 | -19.91 | 36.30 | -0.55 | -2.68 | -673.32 | 24.98 | 11.28 |
| butterfly | JP 2s5s10s fly 50/50 (long belly) | static | full sample, costs x1 | 1990-01-04 | 2026-11-19 | -3.43 | 18.66 | -0.18 | -1.23 | -210.85 | 8.00 | 0.03 |
| butterfly | JP 2s5s10s fly 50/50 (long belly) | meanrev | full sample, costs x1 | 1990-01-04 | 2026-11-19 | -2.34 | 14.39 | -0.16 | -1.10 | -125.10 | 8.43 | 3.77 |
| butterfly | JP 2s5s10s fly 50/50 (long belly) | carry | full sample, costs x1 | 1990-01-04 | 2026-11-19 | -3.54 | 19.24 | -0.18 | -1.25 | -232.69 | 18.52 | 10.55 |
| butterfly | JP 2s5s10s fly 50/50 (long belly) | momentum | full sample, costs x1 | 1990-01-04 | 2026-11-19 | -31.42 | 19.86 | -1.58 | -9.65 | -1,162.41 | 25.14 | 17.22 |
| butterfly | JP 2s5s10s fly PCA-weighted (long belly) | static | full sample, costs x1 | 1990-01-04 | 2026-11-19 | -16.48 | 18.36 | -0.90 | -5.61 | -619.61 | 10.55 | 0.03 |
| butterfly | JP 2s5s10s fly PCA-weighted (long belly) | meanrev | full sample, costs x1 | 1990-01-04 | 2026-11-19 | -8.00 | 13.94 | -0.57 | -3.47 | -317.39 | 10.93 | 3.23 |
| butterfly | JP 2s5s10s fly PCA-weighted (long belly) | carry | full sample, costs x1 | 1990-01-04 | 2026-11-19 | -12.93 | 19.11 | -0.68 | -4.33 | -543.71 | 22.47 | 9.79 |
| butterfly | JP 2s5s10s fly PCA-weighted (long belly) | momentum | full sample, costs x1 | 1990-01-04 | 2026-11-19 | -38.46 | 20.14 | -1.91 | -10.63 | -1,458.48 | 32.13 | 16.84 |
| curve | PL 2s5s steepener | static | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -48.34 | 62.58 | -0.77 | -3.75 | -1,063.14 | 56.01 | 0.00 |
| curve | PL 2s5s steepener | meanrev | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -40.26 | 44.99 | -0.89 | -4.44 | -840.30 | 54.00 | 2.92 |
| curve | PL 2s5s steepener | carry | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -82.83 | 65.89 | -1.26 | -5.90 | -1,755.57 | 95.59 | 5.65 |
| curve | PL 2s5s steepener | momentum | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -163.27 | 79.07 | -2.06 | -9.51 | -3,437.98 | 145.23 | 12.89 |
| curve | PL 2s10s steepener | static | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -34.40 | 73.76 | -0.47 | -2.22 | -858.22 | 51.39 | 0.00 |
| curve | PL 2s10s steepener | meanrev | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -54.10 | 60.22 | -0.90 | -4.29 | -1,129.54 | 45.16 | 2.06 |
| curve | PL 2s10s steepener | carry | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -83.66 | 77.28 | -1.08 | -4.88 | -1,778.84 | 94.99 | 6.71 |
| curve | PL 2s10s steepener | momentum | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -155.49 | 89.09 | -1.75 | -7.64 | -3,277.75 | 137.97 | 13.46 |
| curve | PL 5s10s steepener | static | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -25.76 | 40.77 | -0.63 | -3.15 | -556.15 | 35.58 | 0.00 |
| curve | PL 5s10s steepener | meanrev | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -30.24 | 33.66 | -0.90 | -4.39 | -647.25 | 33.42 | 2.64 |
| curve | PL 5s10s steepener | carry | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -40.15 | 41.64 | -0.96 | -4.62 | -856.42 | 57.14 | 4.79 |
| curve | PL 5s10s steepener | momentum | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -111.76 | 50.82 | -2.20 | -9.63 | -2,343.55 | 101.99 | 14.90 |
| butterfly | PL 2s5s10s fly 50/50 (long belly) | static | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -44.14 | 36.45 | -1.21 | -6.16 | -919.28 | 45.46 | 0.00 |
| butterfly | PL 2s5s10s fly 50/50 (long belly) | meanrev | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -34.16 | 28.18 | -1.21 | -6.27 | -712.87 | 53.17 | 4.46 |
| butterfly | PL 2s5s10s fly 50/50 (long belly) | carry | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -62.57 | 40.59 | -1.54 | -7.10 | -1,311.92 | 75.76 | 5.27 |
| butterfly | PL 2s5s10s fly 50/50 (long belly) | momentum | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -174.31 | 53.42 | -3.26 | -14.06 | -3,650.34 | 150.70 | 18.45 |
| butterfly | PL 2s5s10s fly PCA-weighted (long belly) | static | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -46.95 | 34.38 | -1.37 | -6.79 | -978.02 | 46.97 | 0.00 |
| butterfly | PL 2s5s10s fly PCA-weighted (long belly) | meanrev | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -37.32 | 27.90 | -1.34 | -6.67 | -778.96 | 52.88 | 4.36 |
| butterfly | PL 2s5s10s fly PCA-weighted (long belly) | carry | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -90.85 | 40.19 | -2.26 | -10.10 | -1,900.12 | 101.93 | 9.49 |
| butterfly | PL 2s5s10s fly PCA-weighted (long belly) | momentum | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -181.45 | 52.03 | -3.49 | -14.68 | -3,792.45 | 159.60 | 19.41 |
| cross-country | long FR 10y vs short DE 10y | static | full sample, costs x1 | 2004-11-03 | 2026-11-20 | -6.52 | 47.85 | -0.14 | -0.82 | -268.90 | 6.42 | 0.05 |
| cross-country | long FR 10y vs short DE 10y | meanrev | full sample, costs x1 | 2004-11-03 | 2026-11-20 | 3.33 | 41.63 | 0.08 | 0.47 | -185.12 | 5.55 | 3.31 |
| cross-country | long FR 10y vs short DE 10y | carry | full sample, costs x1 | 2004-11-03 | 2026-11-20 | -2.27 | 47.82 | -0.05 | -0.28 | -216.84 | 10.41 | 5.04 |
| cross-country | long FR 10y vs short DE 10y | momentum | full sample, costs x1 | 2004-11-03 | 2026-11-20 | -29.75 | 47.82 | -0.62 | -3.53 | -730.37 | 20.65 | 17.92 |
| cross-country | long PL 10y vs short DE 10y | static | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -19.97 | 107.46 | -0.19 | -0.93 | -811.21 | 18.58 | 0.00 |
| cross-country | long PL 10y vs short DE 10y | meanrev | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -6.56 | 92.96 | -0.07 | -0.35 | -565.95 | 18.35 | 2.92 |
| cross-country | long PL 10y vs short DE 10y | carry | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -14.60 | 106.58 | -0.14 | -0.68 | -535.93 | 29.61 | 4.70 |
| cross-country | long PL 10y vs short DE 10y | momentum | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -96.86 | 111.79 | -0.87 | -4.06 | -2,067.91 | 58.21 | 17.01 |
| cross-country | long PL 10y vs short FR 10y | static | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -20.54 | 104.02 | -0.20 | -0.99 | -859.78 | 19.37 | 0.00 |
| cross-country | long PL 10y vs short FR 10y | meanrev | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -2.38 | 87.92 | -0.03 | -0.14 | -511.92 | 19.60 | 3.11 |
| cross-country | long PL 10y vs short FR 10y | carry | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -14.81 | 103.76 | -0.14 | -0.70 | -454.72 | 32.75 | 5.46 |
| cross-country | long PL 10y vs short FR 10y | momentum | full sample, costs x1 | 2006-01-06 | 2026-11-20 | -113.39 | 108.29 | -1.05 | -4.91 | -2,391.04 | 59.52 | 16.53 |
| cross-country | long UK 10y vs short DE 10y | static | full sample, costs x1 | 1997-08-07 | 2026-11-19 | -17.20 | 87.41 | -0.20 | -1.79 | -601.26 | 6.02 | 0.03 |
| cross-country | long UK 10y vs short DE 10y | meanrev | full sample, costs x1 | 1997-08-07 | 2026-11-19 | 10.53 | 66.33 | 0.16 | 1.35 | -257.91 | 6.33 | 3.52 |
| cross-country | long UK 10y vs short DE 10y | carry | full sample, costs x1 | 1997-08-07 | 2026-11-19 | 22.40 | 87.44 | 0.26 | 2.31 | -146.99 | 9.96 | 5.29 |
| cross-country | long UK 10y vs short DE 10y | momentum | full sample, costs x1 | 1997-08-07 | 2026-11-19 | -56.55 | 87.47 | -0.65 | -5.25 | -1,667.25 | 19.95 | 18.68 |
| cross-country | long US 10y vs short DE 10y | static | full sample, costs x1 | 1997-08-07 | 2026-11-20 | -6.82 | 103.30 | -0.07 | -0.61 | -391.87 | 4.81 | 0.03 |
| cross-country | long US 10y vs short DE 10y | meanrev | full sample, costs x1 | 1997-08-07 | 2026-11-20 | 3.29 | 81.15 | 0.04 | 0.37 | -300.13 | 4.65 | 2.83 |
| cross-country | long US 10y vs short DE 10y | carry | full sample, costs x1 | 1997-08-07 | 2026-11-20 | 5.92 | 103.27 | 0.06 | 0.51 | -432.79 | 6.99 | 3.65 |
| cross-country | long US 10y vs short DE 10y | momentum | full sample, costs x1 | 1997-08-07 | 2026-11-20 | -41.19 | 103.32 | -0.40 | -3.36 | -1,223.10 | 13.42 | 14.44 |
| cross-country | long JP 10y vs short US 10y | static | full sample, costs x1 | 1990-01-04 | 2026-11-19 | -13.39 | 98.46 | -0.14 | -0.95 | -875.72 | 6.00 | 0.03 |
| cross-country | long JP 10y vs short US 10y | meanrev | full sample, costs x1 | 1990-01-04 | 2026-11-19 | 3.73 | 77.39 | 0.05 | 0.33 | -481.76 | 5.84 | 2.96 |
| cross-country | long JP 10y vs short US 10y | carry | full sample, costs x1 | 1990-01-04 | 2026-11-19 | 4.78 | 98.39 | 0.05 | 0.34 | -502.03 | 7.71 | 2.31 |
| cross-country | long JP 10y vs short US 10y | momentum | full sample, costs x1 | 1990-01-04 | 2026-11-19 | -42.99 | 98.24 | -0.44 | -2.87 | -1,942.05 | 16.86 | 14.56 |
| swap spread | US 10y swap spread (long = buy UST, pay fixed) | static | full sample, costs x1 | 2000-07-03 | 2016-10-28 | -16.34 | 85.09 | -0.19 | -1.98 | -288.09 | 4.01 | 0.06 |
| swap spread | US 10y swap spread (long = buy UST, pay fixed) | meanrev | full sample, costs x1 | 2000-07-03 | 2016-10-28 | 18.21 | 64.59 | 0.28 | 2.42 | -75.86 | 4.44 | 4.96 |
| swap spread | US 10y swap spread (long = buy UST, pay fixed) | carry | full sample, costs x1 | 2000-07-03 | 2016-10-28 | 10.89 | 85.00 | 0.13 | 1.25 | -121.78 | 6.46 | 4.96 |
| swap spread | US 10y swap spread (long = buy UST, pay fixed) | momentum | full sample, costs x1 | 2000-07-03 | 2016-10-28 | -57.52 | 83.99 | -0.68 | -5.26 | -992.74 | 15.90 | 24.08 |
| swap spread | UK 10y OIS spread (long = buy gilt, pay fixed OIS) | static | full sample, costs x1 | 2016-01-04 | 2026-11-19 | 0.97 | 35.87 | 0.03 | 0.18 | -80.50 | 5.60 | 0.09 |
| swap spread | UK 10y OIS spread (long = buy gilt, pay fixed OIS) | meanrev | full sample, costs x1 | 2016-01-04 | 2026-11-19 | -6.21 | 31.94 | -0.19 | -1.30 | -73.22 | 6.12 | 3.03 |
| swap spread | UK 10y OIS spread (long = buy gilt, pay fixed OIS) | carry | full sample, costs x1 | 2016-01-04 | 2026-11-19 | 0.97 | 35.87 | 0.03 | 0.18 | -80.50 | 5.60 | 0.09 |
| swap spread | UK 10y OIS spread (long = buy gilt, pay fixed OIS) | momentum | full sample, costs x1 | 2016-01-04 | 2026-11-19 | -25.69 | 35.78 | -0.72 | -3.90 | -299.73 | 17.96 | 17.93 |
| breakeven | US 10y breakeven (long TIPS, short nominal) | static | full sample, costs x1 | 2003-01-02 | 2026-11-20 | -7.01 | 53.18 | -0.13 | -0.62 | -475.67 | 10.00 | 0.04 |
| breakeven | US 10y breakeven (long TIPS, short nominal) | meanrev | full sample, costs x1 | 2003-01-02 | 2026-11-20 | 3.42 | 42.71 | 0.08 | 0.37 | -245.82 | 9.89 | 3.22 |
| breakeven | US 10y breakeven (long TIPS, short nominal) | carry | full sample, costs x1 | 2003-01-02 | 2026-11-20 | -26.15 | 53.28 | -0.49 | -2.22 | -686.42 | 17.01 | 5.65 |
| breakeven | US 10y breakeven (long TIPS, short nominal) | momentum | full sample, costs x1 | 2003-01-02 | 2026-11-20 | -17.31 | 53.51 | -0.32 | -1.50 | -465.60 | 24.65 | 12.02 |
| breakeven | UK 10y breakeven (long linker, short gilt) | static | full sample, costs x1 | 1990-02-28 | 2026-11-19 | -34.81 | 66.00 | -0.53 | -3.02 | -1,414.71 | 11.25 | 0.03 |
| breakeven | UK 10y breakeven (long linker, short gilt) | meanrev | full sample, costs x1 | 1990-02-28 | 2026-11-19 | -6.82 | 51.23 | -0.13 | -0.73 | -435.39 | 10.37 | 2.40 |
| breakeven | UK 10y breakeven (long linker, short gilt) | carry | full sample, costs x1 | 1990-02-28 | 2026-11-19 | -6.20 | 65.76 | -0.09 | -0.56 | -530.88 | 13.08 | 1.33 |
| breakeven | UK 10y breakeven (long linker, short gilt) | momentum | full sample, costs x1 | 1990-02-28 | 2026-11-19 | -46.19 | 65.36 | -0.71 | -4.05 | -1,751.75 | 32.06 | 14.95 |
| credit | US Baa vs 20y Treasury (long credit, rates-hedged) | static | full sample, costs x1 | 1993-10-01 | 2026-11-19 | 7.40 | 38.04 | 0.19 | 0.76 | -389.52 | 5.20 | 0.00 |
| credit | US Baa vs 20y Treasury (long credit, rates-hedged) | meanrev | full sample, costs x1 | 1993-10-01 | 2026-11-19 | -14.30 | 32.91 | -0.43 | -1.67 | -654.67 | 4.94 | 2.17 |
| credit | US Baa vs 20y Treasury (long credit, rates-hedged) | carry | full sample, costs x1 | 1993-10-01 | 2026-11-19 | 7.40 | 38.04 | 0.19 | 0.76 | -389.52 | 5.20 | 0.00 |
| credit | US Baa vs 20y Treasury (long credit, rates-hedged) | momentum | full sample, costs x1 | 1993-10-01 | 2026-11-19 | 20.46 | 38.09 | 0.54 | 2.14 | -175.02 | 11.91 | 10.35 |
| carry | cross-country 10y carry/vol (long best, short worst) | carry | full sample, costs x1 | 2004-11-04 | 2026-11-19 | 15.49 | 82.00 | 0.19 | 1.20 | -200.03 | 1.96 | 0.05 |

## Mean reversion: in-sample choice, out-of-sample and walk-forward

| family | strategy | signal | test | start | end | ann_return_bp | ann_vol_bp | sharpe | t_nw | max_dd_bp | cost_bp_per_year | turnover_per_year | params |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| curve | US 2s10s steepener | meanrev | in-sample (first half, chosen params) | 1990-01-02 | 2008-06-11 | -26.28 | 48.33 | -0.54 | -2.31 | -554.97 | 4.20 | 3.15 | {'lookback': 26, 'entry': 1.5, 'exit': 0.0} |
| curve | US 2s10s steepener | meanrev | out-of-sample (second half) | 2008-06-12 | 2026-11-20 | -10.26 | 55.34 | -0.19 | -0.88 | -360.55 | 4.42 | 3.42 | {'lookback': 26, 'entry': 1.5, 'exit': 0.0} |
| curve | US 2s10s steepener | meanrev | walk-forward OOS | 1994-01-03 | 2026-11-20 | -21.08 | 49.32 | -0.43 | -2.59 | -903.17 | 3.11 | 1.52 | re-selected yearly |
| curve | US 5s30s steepener | meanrev | in-sample (first half, chosen params) | 1993-10-01 | 2012-04-19 | -0.60 | 40.05 | -0.01 | -0.06 | -313.08 | 3.64 | 2.26 | {'lookback': 52, 'entry': 1.5, 'exit': 0.5} |
| curve | US 5s30s steepener | meanrev | out-of-sample (second half) | 2012-04-20 | 2026-11-20 | 4.29 | 43.88 | 0.10 | 0.40 | -222.40 | 5.30 | 3.22 | {'lookback': 52, 'entry': 1.5, 'exit': 0.5} |
| curve | US 5s30s steepener | meanrev | walk-forward OOS | 1997-01-02 | 2026-11-20 | -14.37 | 56.33 | -0.26 | -1.42 | -655.82 | 4.42 | 2.38 | re-selected yearly |
| butterfly | US 2s5s10s fly 50/50 (long belly) | meanrev | in-sample (first half, chosen params) | 1990-01-02 | 2008-06-11 | 4.70 | 16.46 | 0.29 | 1.66 | -37.17 | 2.29 | 1.46 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| butterfly | US 2s5s10s fly 50/50 (long belly) | meanrev | out-of-sample (second half) | 2008-06-12 | 2026-11-20 | 2.43 | 18.85 | 0.13 | 0.64 | -53.26 | 2.63 | 1.08 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| butterfly | US 2s5s10s fly 50/50 (long belly) | meanrev | walk-forward OOS | 1994-01-03 | 2026-11-20 | 2.91 | 18.16 | 0.16 | 1.13 | -58.22 | 2.67 | 1.52 | re-selected yearly |
| butterfly | US 2s5s10s fly PCA-weighted (long belly) | meanrev | in-sample (first half, chosen params) | 1990-01-02 | 2008-06-11 | 5.92 | 19.41 | 0.31 | 1.67 | -55.53 | 7.98 | 9.60 | {'lookback': 26, 'entry': 1.0, 'exit': 0.0} |
| butterfly | US 2s5s10s fly PCA-weighted (long belly) | meanrev | out-of-sample (second half) | 2008-06-12 | 2026-11-20 | -3.95 | 20.39 | -0.19 | -1.00 | -120.28 | 6.12 | 5.10 | {'lookback': 26, 'entry': 1.0, 'exit': 0.0} |
| butterfly | US 2s5s10s fly PCA-weighted (long belly) | meanrev | walk-forward OOS | 1994-01-03 | 2026-11-20 | -1.48 | 19.49 | -0.08 | -0.54 | -122.02 | 6.47 | 6.48 | re-selected yearly |
| curve | DE 2s10s steepener | meanrev | in-sample (first half, chosen params) | 1997-08-07 | 2012-03-23 | -6.25 | 54.72 | -0.11 | -0.50 | -351.60 | 4.71 | 1.37 | {'lookback': 104, 'entry': 1.5, 'exit': 0.0} |
| curve | DE 2s10s steepener | meanrev | out-of-sample (second half) | 2012-03-26 | 2026-11-20 | -15.34 | 42.25 | -0.36 | -1.46 | -304.93 | 5.10 | 1.43 | {'lookback': 104, 'entry': 1.5, 'exit': 0.0} |
| curve | DE 2s10s steepener | meanrev | walk-forward OOS | 2001-01-02 | 2026-11-20 | -14.91 | 49.78 | -0.30 | -1.68 | -485.91 | 5.12 | 1.39 | re-selected yearly |
| curve | DE 5s30s steepener | meanrev | in-sample (first half, chosen params) | 2000-08-01 | 2013-09-17 | 1.33 | 41.19 | 0.03 | 0.12 | -206.96 | 4.51 | 1.98 | {'lookback': 52, 'entry': 2.0, 'exit': 0.5} |
| curve | DE 5s30s steepener | meanrev | out-of-sample (second half) | 2013-09-18 | 2026-11-20 | -6.79 | 39.30 | -0.17 | -0.72 | -148.97 | 5.16 | 2.05 | {'lookback': 52, 'entry': 2.0, 'exit': 0.5} |
| curve | DE 5s30s steepener | meanrev | walk-forward OOS | 2004-01-02 | 2026-11-20 | -5.68 | 43.90 | -0.13 | -0.68 | -202.25 | 6.19 | 3.10 | re-selected yearly |
| butterfly | DE 2s5s10s fly 50/50 (long belly) | meanrev | in-sample (first half, chosen params) | 1997-08-07 | 2012-03-23 | 3.08 | 15.31 | 0.20 | 0.95 | -26.39 | 2.78 | 1.30 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| butterfly | DE 2s5s10s fly 50/50 (long belly) | meanrev | out-of-sample (second half) | 2012-03-26 | 2026-11-20 | -1.44 | 13.56 | -0.11 | -0.53 | -36.89 | 3.71 | 1.30 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| butterfly | DE 2s5s10s fly 50/50 (long belly) | meanrev | walk-forward OOS | 2001-01-02 | 2026-11-20 | 0.79 | 13.45 | 0.06 | 0.37 | -59.50 | 3.36 | 1.47 | re-selected yearly |
| butterfly | DE 2s5s10s fly PCA-weighted (long belly) | meanrev | in-sample (first half, chosen params) | 1997-08-07 | 2012-03-23 | -0.72 | 19.63 | -0.04 | -0.20 | -78.17 | 7.24 | 6.63 | {'lookback': 26, 'entry': 1.5, 'exit': 0.5} |
| butterfly | DE 2s5s10s fly PCA-weighted (long belly) | meanrev | out-of-sample (second half) | 2012-03-26 | 2026-11-20 | -5.63 | 12.88 | -0.44 | -2.10 | -96.47 | 6.59 | 5.73 | {'lookback': 26, 'entry': 1.5, 'exit': 0.5} |
| butterfly | DE 2s5s10s fly PCA-weighted (long belly) | meanrev | walk-forward OOS | 2001-01-02 | 2026-11-20 | -5.12 | 16.33 | -0.31 | -2.31 | -152.57 | 5.88 | 4.17 | re-selected yearly |
| curve | FR 2s10s steepener | meanrev | in-sample (first half, chosen params) | 2004-11-03 | 2015-11-11 | -8.81 | 50.52 | -0.17 | -0.54 | -280.23 | 6.71 | 2.09 | {'lookback': 104, 'entry': 1.0, 'exit': 0.0} |
| curve | FR 2s10s steepener | meanrev | out-of-sample (second half) | 2015-11-12 | 2026-11-20 | -24.13 | 49.78 | -0.48 | -1.94 | -357.05 | 6.40 | 1.18 | {'lookback': 104, 'entry': 1.0, 'exit': 0.0} |
| curve | FR 2s10s steepener | meanrev | walk-forward OOS | 2008-01-02 | 2026-11-20 | -20.09 | 53.41 | -0.38 | -1.76 | -451.23 | 6.93 | 1.80 | re-selected yearly |
| curve | FR 5s30s steepener | meanrev | in-sample (first half, chosen params) | 2006-10-02 | 2016-10-26 | 13.15 | 43.31 | 0.30 | 0.93 | -113.32 | 7.10 | 2.88 | {'lookback': 52, 'entry': 2.0, 'exit': 0.5} |
| curve | FR 5s30s steepener | meanrev | out-of-sample (second half) | 2016-10-27 | 2026-11-20 | -7.68 | 40.76 | -0.19 | -0.75 | -141.37 | 7.43 | 2.19 | {'lookback': 52, 'entry': 2.0, 'exit': 0.5} |
| curve | FR 5s30s steepener | meanrev | walk-forward OOS | 2010-01-04 | 2026-11-20 | -3.69 | 39.28 | -0.09 | -0.44 | -179.23 | 7.17 | 2.43 | re-selected yearly |
| butterfly | FR 2s5s10s fly 50/50 (long belly) | meanrev | in-sample (first half, chosen params) | 2004-11-03 | 2015-11-11 | 6.87 | 21.40 | 0.32 | 1.27 | -57.32 | 5.47 | 2.27 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| butterfly | FR 2s5s10s fly 50/50 (long belly) | meanrev | out-of-sample (second half) | 2015-11-12 | 2026-11-20 | 1.46 | 15.23 | 0.10 | 0.53 | -22.78 | 2.99 | 1.09 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| butterfly | FR 2s5s10s fly 50/50 (long belly) | meanrev | walk-forward OOS | 2008-01-02 | 2026-11-20 | 2.50 | 20.63 | 0.12 | 0.70 | -59.11 | 5.02 | 2.22 | re-selected yearly |
| butterfly | FR 2s5s10s fly PCA-weighted (long belly) | meanrev | in-sample (first half, chosen params) | 2004-11-03 | 2015-11-11 | 2.72 | 24.94 | 0.11 | 0.48 | -68.87 | 8.86 | 5.17 | {'lookback': 26, 'entry': 2.0, 'exit': 0.5} |
| butterfly | FR 2s5s10s fly PCA-weighted (long belly) | meanrev | out-of-sample (second half) | 2015-11-12 | 2026-11-20 | 0.87 | 15.91 | 0.05 | 0.27 | -37.58 | 7.73 | 4.90 | {'lookback': 26, 'entry': 2.0, 'exit': 0.5} |
| butterfly | FR 2s5s10s fly PCA-weighted (long belly) | meanrev | walk-forward OOS | 2008-01-02 | 2026-11-20 | 1.06 | 22.72 | 0.05 | 0.28 | -118.16 | 8.21 | 4.82 | re-selected yearly |
| curve | UK 2s10s steepener | meanrev | in-sample (first half, chosen params) | 1990-01-02 | 2008-06-11 | 3.07 | 51.64 | 0.06 | 0.25 | -298.16 | 4.29 | 1.25 | {'lookback': 104, 'entry': 1.5, 'exit': 0.5} |
| curve | UK 2s10s steepener | meanrev | out-of-sample (second half) | 2008-06-12 | 2026-11-19 | -23.97 | 45.10 | -0.53 | -2.03 | -553.32 | 4.37 | 1.14 | {'lookback': 104, 'entry': 1.5, 'exit': 0.5} |
| curve | UK 2s10s steepener | meanrev | walk-forward OOS | 1994-01-04 | 2026-11-19 | -19.42 | 43.67 | -0.44 | -2.32 | -776.31 | 5.11 | 2.01 | re-selected yearly |
| curve | UK 5s30s steepener | meanrev | in-sample (first half, chosen params) | 2016-01-04 | 2021-06-11 | 2.76 | 23.17 | 0.12 | 0.33 | -51.59 | 3.15 | 0.92 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| curve | UK 5s30s steepener | meanrev | out-of-sample (second half) | 2021-06-14 | 2026-11-19 | 29.55 | 55.44 | 0.53 | 1.45 | -100.01 | 4.80 | 1.66 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| curve | UK 5s30s steepener | meanrev | walk-forward OOS | 2020-01-02 | 2026-11-19 | 10.72 | 52.69 | 0.20 | 0.63 | -100.01 | 5.23 | 2.18 | re-selected yearly |
| butterfly | UK 2s5s10s fly 50/50 (long belly) | meanrev | in-sample (first half, chosen params) | 1990-01-02 | 2008-06-11 | -3.18 | 11.51 | -0.28 | -1.20 | -109.05 | 2.86 | 0.92 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| butterfly | UK 2s5s10s fly 50/50 (long belly) | meanrev | out-of-sample (second half) | 2008-06-12 | 2026-11-19 | -3.23 | 10.57 | -0.31 | -1.10 | -92.05 | 3.95 | 1.41 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| butterfly | UK 2s5s10s fly 50/50 (long belly) | meanrev | walk-forward OOS | 1994-01-04 | 2026-11-19 | -5.95 | 11.35 | -0.52 | -2.77 | -214.96 | 3.64 | 1.43 | re-selected yearly |
| butterfly | UK 2s5s10s fly PCA-weighted (long belly) | meanrev | in-sample (first half, chosen params) | 1990-01-02 | 2008-06-11 | -2.19 | 9.30 | -0.24 | -1.06 | -63.37 | 2.93 | 1.36 | {'lookback': 104, 'entry': 2.0, 'exit': 0.5} |
| butterfly | UK 2s5s10s fly PCA-weighted (long belly) | meanrev | out-of-sample (second half) | 2008-06-12 | 2026-11-19 | -1.81 | 8.62 | -0.21 | -0.71 | -50.60 | 3.41 | 1.30 | {'lookback': 104, 'entry': 2.0, 'exit': 0.5} |
| butterfly | UK 2s5s10s fly PCA-weighted (long belly) | meanrev | walk-forward OOS | 1994-01-04 | 2026-11-19 | -4.16 | 9.65 | -0.43 | -2.22 | -138.64 | 4.23 | 1.73 | re-selected yearly |
| curve | JP 2s10s steepener | meanrev | in-sample (first half, chosen params) | 1990-01-04 | 2008-05-20 | -4.09 | 34.94 | -0.12 | -0.46 | -205.29 | 9.36 | 5.33 | {'lookback': 26, 'entry': 1.5, 'exit': 0.5} |
| curve | JP 2s10s steepener | meanrev | out-of-sample (second half) | 2008-05-21 | 2026-11-19 | -8.93 | 20.10 | -0.44 | -2.03 | -215.52 | 9.35 | 5.35 | {'lookback': 26, 'entry': 1.5, 'exit': 0.5} |
| curve | JP 2s10s steepener | meanrev | walk-forward OOS | 1994-01-04 | 2026-11-19 | -7.36 | 26.39 | -0.28 | -1.57 | -299.69 | 9.00 | 5.11 | re-selected yearly |
| curve | JP 5s30s steepener | meanrev | in-sample (first half, chosen params) | 1999-09-02 | 2013-04-01 | 2.65 | 21.49 | 0.12 | 0.39 | -64.90 | 4.31 | 0.81 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| curve | JP 5s30s steepener | meanrev | out-of-sample (second half) | 2013-04-02 | 2026-11-19 | -18.37 | 33.56 | -0.55 | -2.38 | -280.66 | 8.11 | 0.51 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| curve | JP 5s30s steepener | meanrev | walk-forward OOS | 2003-01-06 | 2026-11-19 | -6.32 | 28.32 | -0.22 | -1.12 | -217.37 | 6.21 | 0.96 | re-selected yearly |
| butterfly | JP 2s5s10s fly 50/50 (long belly) | meanrev | in-sample (first half, chosen params) | 1990-01-04 | 2008-05-20 | 2.68 | 15.21 | 0.18 | 0.83 | -51.98 | 5.99 | 2.72 | {'lookback': 52, 'entry': 2.0, 'exit': 0.5} |
| butterfly | JP 2s5s10s fly 50/50 (long belly) | meanrev | out-of-sample (second half) | 2008-05-21 | 2026-11-19 | -2.67 | 7.79 | -0.34 | -1.85 | -70.89 | 6.11 | 2.87 | {'lookback': 52, 'entry': 2.0, 'exit': 0.5} |
| butterfly | JP 2s5s10s fly 50/50 (long belly) | meanrev | walk-forward OOS | 1994-01-04 | 2026-11-19 | -1.88 | 11.39 | -0.17 | -1.12 | -101.17 | 6.14 | 2.49 | re-selected yearly |
| butterfly | JP 2s5s10s fly PCA-weighted (long belly) | meanrev | in-sample (first half, chosen params) | 1990-01-04 | 2008-05-20 | -2.70 | 15.73 | -0.17 | -0.66 | -99.06 | 7.46 | 2.01 | {'lookback': 52, 'entry': 2.0, 'exit': 0.0} |
| butterfly | JP 2s5s10s fly PCA-weighted (long belly) | meanrev | out-of-sample (second half) | 2008-05-21 | 2026-11-19 | -8.33 | 10.89 | -0.77 | -4.08 | -160.78 | 10.25 | 2.27 | {'lookback': 52, 'entry': 2.0, 'exit': 0.0} |
| butterfly | JP 2s5s10s fly PCA-weighted (long belly) | meanrev | walk-forward OOS | 1994-01-04 | 2026-11-19 | -6.95 | 13.45 | -0.52 | -3.24 | -250.19 | 10.53 | 2.80 | re-selected yearly |
| curve | PL 2s5s steepener | meanrev | in-sample (first half, chosen params) | 2006-01-06 | 2016-06-17 | -25.37 | 34.53 | -0.73 | -2.67 | -296.44 | 31.50 | 1.24 | {'lookback': 104, 'entry': 2.0, 'exit': 0.5} |
| curve | PL 2s5s steepener | meanrev | out-of-sample (second half) | 2016-06-24 | 2026-11-20 | -15.27 | 45.90 | -0.33 | -1.15 | -186.50 | 41.70 | 1.92 | {'lookback': 104, 'entry': 2.0, 'exit': 0.5} |
| curve | PL 2s5s steepener | meanrev | walk-forward OOS | 2010-01-08 | 2026-11-20 | -20.27 | 44.65 | -0.45 | -2.08 | -372.67 | 38.19 | 1.54 | re-selected yearly |
| curve | PL 2s10s steepener | meanrev | in-sample (first half, chosen params) | 2006-01-06 | 2016-04-29 | -34.82 | 47.96 | -0.73 | -2.52 | -396.01 | 32.15 | 0.87 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| curve | PL 2s10s steepener | meanrev | out-of-sample (second half) | 2016-05-06 | 2026-11-20 | -32.46 | 68.37 | -0.47 | -1.64 | -404.14 | 41.93 | 1.14 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| curve | PL 2s10s steepener | meanrev | walk-forward OOS | 2010-01-08 | 2026-11-20 | -32.12 | 61.91 | -0.52 | -2.27 | -562.55 | 38.54 | 1.07 | re-selected yearly |
| curve | PL 5s10s steepener | meanrev | in-sample (first half, chosen params) | 2006-01-06 | 2016-04-29 | -8.60 | 22.06 | -0.39 | -1.25 | -108.78 | 19.64 | 2.04 | {'lookback': 104, 'entry': 2.0, 'exit': 0.5} |
| curve | PL 5s10s steepener | meanrev | out-of-sample (second half) | 2016-05-06 | 2026-11-20 | -9.17 | 26.13 | -0.35 | -1.20 | -129.45 | 11.53 | 0.66 | {'lookback': 104, 'entry': 2.0, 'exit': 0.5} |
| curve | PL 5s10s steepener | meanrev | walk-forward OOS | 2010-01-08 | 2026-11-20 | -7.03 | 23.91 | -0.29 | -1.26 | -166.54 | 14.14 | 1.36 | re-selected yearly |
| butterfly | PL 2s5s10s fly 50/50 (long belly) | meanrev | in-sample (first half, chosen params) | 2006-01-06 | 2016-04-29 | -14.29 | 22.53 | -0.63 | -2.55 | -152.92 | 30.11 | 1.94 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| butterfly | PL 2s5s10s fly 50/50 (long belly) | meanrev | out-of-sample (second half) | 2016-05-06 | 2026-11-20 | -16.81 | 25.31 | -0.66 | -2.23 | -188.38 | 23.46 | 1.23 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| butterfly | PL 2s5s10s fly 50/50 (long belly) | meanrev | walk-forward OOS | 2010-01-08 | 2026-11-20 | -15.64 | 25.11 | -0.62 | -2.85 | -292.26 | 27.28 | 1.66 | re-selected yearly |
| butterfly | PL 2s5s10s fly PCA-weighted (long belly) | meanrev | in-sample (first half, chosen params) | 2006-01-06 | 2016-04-29 | -19.59 | 22.66 | -0.86 | -3.35 | -212.28 | 31.79 | 1.75 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| butterfly | PL 2s5s10s fly PCA-weighted (long belly) | meanrev | out-of-sample (second half) | 2016-05-06 | 2026-11-20 | -25.44 | 32.04 | -0.79 | -2.77 | -282.84 | 29.11 | 0.95 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| butterfly | PL 2s5s10s fly PCA-weighted (long belly) | meanrev | walk-forward OOS | 2010-01-08 | 2026-11-20 | -26.54 | 30.07 | -0.88 | -4.04 | -470.35 | 33.85 | 1.36 | re-selected yearly |
| cross-country | long FR 10y vs short DE 10y | meanrev | in-sample (first half, chosen params) | 2004-11-03 | 2015-11-09 | 5.58 | 48.19 | 0.12 | 0.47 | -184.50 | 6.25 | 4.36 | {'lookback': 52, 'entry': 1.5, 'exit': 0.5} |
| cross-country | long FR 10y vs short DE 10y | meanrev | out-of-sample (second half) | 2015-11-10 | 2026-11-20 | 1.31 | 30.91 | 0.04 | 0.18 | -89.35 | 5.01 | 3.17 | {'lookback': 52, 'entry': 1.5, 'exit': 0.5} |
| cross-country | long FR 10y vs short DE 10y | meanrev | walk-forward OOS | 2008-01-02 | 2026-11-20 | 1.31 | 43.10 | 0.03 | 0.16 | -187.13 | 6.69 | 4.71 | re-selected yearly |
| cross-country | long PL 10y vs short DE 10y | meanrev | in-sample (first half, chosen params) | 2006-01-06 | 2016-04-29 | 22.61 | 67.24 | 0.34 | 1.25 | -94.37 | 19.37 | 4.56 | {'lookback': 26, 'entry': 2.0, 'exit': 0.5} |
| cross-country | long PL 10y vs short DE 10y | meanrev | out-of-sample (second half) | 2016-05-06 | 2026-11-20 | -5.47 | 78.28 | -0.07 | -0.23 | -425.81 | 17.39 | 4.17 | {'lookback': 26, 'entry': 2.0, 'exit': 0.5} |
| cross-country | long PL 10y vs short DE 10y | meanrev | walk-forward OOS | 2010-01-08 | 2026-11-20 | 4.21 | 72.64 | 0.06 | 0.24 | -425.81 | 17.42 | 4.21 | re-selected yearly |
| cross-country | long PL 10y vs short FR 10y | meanrev | in-sample (first half, chosen params) | 2006-01-06 | 2016-04-29 | 35.37 | 63.84 | 0.55 | 2.03 | -69.81 | 20.67 | 4.75 | {'lookback': 26, 'entry': 2.0, 'exit': 0.5} |
| cross-country | long PL 10y vs short FR 10y | meanrev | out-of-sample (second half) | 2016-05-06 | 2026-11-20 | -2.41 | 73.54 | -0.03 | -0.11 | -414.44 | 18.13 | 4.17 | {'lookback': 26, 'entry': 2.0, 'exit': 0.5} |
| cross-country | long PL 10y vs short FR 10y | meanrev | walk-forward OOS | 2010-01-08 | 2026-11-20 | 9.68 | 72.97 | 0.13 | 0.56 | -414.44 | 19.18 | 4.33 | re-selected yearly |
| cross-country | long UK 10y vs short DE 10y | meanrev | in-sample (first half, chosen params) | 1997-08-07 | 2012-03-23 | 28.27 | 68.00 | 0.42 | 2.74 | -78.35 | 12.41 | 11.76 | {'lookback': 26, 'entry': 1.0, 'exit': 0.5} |
| cross-country | long UK 10y vs short DE 10y | meanrev | out-of-sample (second half) | 2012-03-26 | 2026-11-19 | 17.68 | 66.63 | 0.27 | 1.53 | -127.04 | 10.65 | 9.56 | {'lookback': 26, 'entry': 1.0, 'exit': 0.5} |
| cross-country | long UK 10y vs short DE 10y | meanrev | walk-forward OOS | 2001-01-02 | 2026-11-19 | 16.95 | 65.13 | 0.26 | 2.10 | -127.04 | 10.26 | 9.20 | re-selected yearly |
| cross-country | long US 10y vs short DE 10y | meanrev | in-sample (first half, chosen params) | 1997-08-07 | 2012-03-21 | 16.93 | 76.80 | 0.22 | 1.44 | -166.04 | 5.13 | 4.45 | {'lookback': 26, 'entry': 2.0, 'exit': 0.5} |
| cross-country | long US 10y vs short DE 10y | meanrev | out-of-sample (second half) | 2012-03-22 | 2026-11-20 | 2.94 | 63.06 | 0.05 | 0.28 | -271.66 | 5.20 | 4.30 | {'lookback': 26, 'entry': 2.0, 'exit': 0.5} |
| cross-country | long US 10y vs short DE 10y | meanrev | walk-forward OOS | 2001-01-02 | 2026-11-20 | 1.48 | 78.23 | 0.02 | 0.16 | -313.31 | 6.00 | 5.37 | re-selected yearly |
| cross-country | long JP 10y vs short US 10y | meanrev | in-sample (first half, chosen params) | 1990-01-04 | 2008-05-19 | 40.58 | 74.85 | 0.54 | 2.50 | -182.41 | 5.76 | 4.19 | {'lookback': 26, 'entry': 2.0, 'exit': 0.0} |
| cross-country | long JP 10y vs short US 10y | meanrev | out-of-sample (second half) | 2008-05-20 | 2026-11-19 | -13.11 | 76.82 | -0.17 | -0.92 | -491.67 | 6.89 | 3.57 | {'lookback': 26, 'entry': 2.0, 'exit': 0.0} |
| cross-country | long JP 10y vs short US 10y | meanrev | walk-forward OOS | 1994-01-04 | 2026-11-19 | 8.13 | 76.61 | 0.11 | 0.70 | -443.14 | 7.21 | 4.87 | re-selected yearly |
| swap spread | US 10y swap spread (long = buy UST, pay fixed) | meanrev | in-sample (first half, chosen params) | 2000-07-03 | 2008-08-29 | 26.78 | 58.73 | 0.46 | 2.40 | -63.03 | 5.39 | 7.36 | {'lookback': 26, 'entry': 1.5, 'exit': 0.5} |
| swap spread | US 10y swap spread (long = buy UST, pay fixed) | meanrev | out-of-sample (second half) | 2008-09-02 | 2016-10-28 | 24.66 | 54.84 | 0.45 | 2.67 | -66.25 | 6.01 | 9.08 | {'lookback': 26, 'entry': 1.5, 'exit': 0.5} |
| swap spread | US 10y swap spread (long = buy UST, pay fixed) | meanrev | walk-forward OOS | 2004-01-02 | 2016-10-28 | 27.01 | 53.67 | 0.50 | 3.80 | -66.25 | 6.79 | 10.30 | re-selected yearly |
| swap spread | UK 10y OIS spread (long = buy gilt, pay fixed OIS) | meanrev | in-sample (first half, chosen params) | 2016-01-04 | 2021-06-11 | 0.38 | 21.49 | 0.02 | 0.08 | -28.79 | 4.12 | 4.05 | {'lookback': 26, 'entry': 2.0, 'exit': 0.5} |
| swap spread | UK 10y OIS spread (long = buy gilt, pay fixed OIS) | meanrev | out-of-sample (second half) | 2021-06-14 | 2026-11-19 | 2.66 | 24.45 | 0.11 | 0.48 | -37.81 | 4.90 | 4.42 | {'lookback': 26, 'entry': 2.0, 'exit': 0.5} |
| swap spread | UK 10y OIS spread (long = buy gilt, pay fixed OIS) | meanrev | walk-forward OOS | 2020-01-02 | 2026-11-19 | 2.79 | 25.68 | 0.11 | 0.56 | -37.81 | 4.88 | 4.36 | re-selected yearly |
| breakeven | US 10y breakeven (long TIPS, short nominal) | meanrev | in-sample (first half, chosen params) | 2003-01-02 | 2014-12-10 | 17.34 | 49.02 | 0.35 | 1.13 | -218.09 | 10.37 | 2.93 | {'lookback': 104, 'entry': 1.0, 'exit': 0.0} |
| breakeven | US 10y breakeven (long TIPS, short nominal) | meanrev | out-of-sample (second half) | 2014-12-11 | 2026-11-20 | -2.78 | 43.64 | -0.06 | -0.22 | -266.12 | 11.51 | 2.51 | {'lookback': 104, 'entry': 1.0, 'exit': 0.0} |
| breakeven | US 10y breakeven (long TIPS, short nominal) | meanrev | walk-forward OOS | 2007-01-02 | 2026-11-20 | 5.94 | 46.74 | 0.13 | 0.53 | -291.08 | 9.56 | 2.36 | re-selected yearly |
| breakeven | UK 10y breakeven (long linker, short gilt) | meanrev | in-sample (first half, chosen params) | 1990-02-28 | 2008-07-10 | -0.91 | 33.82 | -0.03 | -0.11 | -197.54 | 4.96 | 0.93 | {'lookback': 104, 'entry': 2.0, 'exit': 0.5} |
| breakeven | UK 10y breakeven (long linker, short gilt) | meanrev | out-of-sample (second half) | 2008-07-11 | 2026-11-19 | 7.65 | 33.47 | 0.23 | 0.72 | -154.54 | 5.72 | 1.14 | {'lookback': 104, 'entry': 2.0, 'exit': 0.5} |
| breakeven | UK 10y breakeven (long linker, short gilt) | meanrev | walk-forward OOS | 1994-01-04 | 2026-11-19 | 1.62 | 38.64 | 0.04 | 0.22 | -268.90 | 6.30 | 1.40 | re-selected yearly |
| credit | US Baa vs 20y Treasury (long credit, rates-hedged) | meanrev | in-sample (first half, chosen params) | 1993-10-01 | 2010-04-23 | -7.02 | 32.59 | -0.22 | -0.55 | -411.87 | 3.53 | 0.85 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| credit | US Baa vs 20y Treasury (long credit, rates-hedged) | meanrev | out-of-sample (second half) | 2010-04-26 | 2026-11-19 | 9.27 | 23.81 | 0.39 | 1.06 | -101.12 | 2.28 | 0.60 | {'lookback': 104, 'entry': 2.0, 'exit': 0.0} |
| credit | US Baa vs 20y Treasury (long credit, rates-hedged) | meanrev | walk-forward OOS | 1997-01-02 | 2026-11-19 | -3.45 | 29.46 | -0.12 | -0.40 | -494.88 | 3.13 | 1.07 | re-selected yearly |

## Cost sensitivity (full sample)

| strategy | signal | full sample, costs x0 | full sample, costs x1 | full sample, costs x2 |
|---|---|---:|---:|---:|
| DE 2s10s steepener | carry | 0.11 | -0.04 | -0.19 |
| DE 2s10s steepener | meanrev | -0.28 | -0.38 | -0.48 |
| DE 2s10s steepener | momentum | 0.36 | 0.14 | -0.09 |
| DE 2s10s steepener | static |  | -0.32 |  |
| DE 2s5s10s fly 50/50 (long belly) | carry | 0.15 | -0.22 | -0.56 |
| DE 2s5s10s fly 50/50 (long belly) | meanrev | 0.19 | -0.10 | -0.38 |
| DE 2s5s10s fly 50/50 (long belly) | momentum | -0.28 | -0.98 | -1.58 |
| DE 2s5s10s fly 50/50 (long belly) | static |  | -0.01 |  |
| DE 2s5s10s fly PCA-weighted (long belly) | carry | -0.01 | -0.48 | -0.91 |
| DE 2s5s10s fly PCA-weighted (long belly) | meanrev | 0.03 | -0.30 | -0.61 |
| DE 2s5s10s fly PCA-weighted (long belly) | momentum | -0.20 | -0.95 | -1.58 |
| DE 2s5s10s fly PCA-weighted (long belly) | static |  | -0.22 |  |
| DE 5s30s steepener | carry | 0.20 | 0.03 | -0.15 |
| DE 5s30s steepener | meanrev | -0.07 | -0.20 | -0.32 |
| DE 5s30s steepener | momentum | 0.13 | -0.18 | -0.48 |
| DE 5s30s steepener | static |  | 0.04 |  |
| FR 2s10s steepener | carry | 0.64 | 0.45 | 0.25 |
| FR 2s10s steepener | meanrev | -0.30 | -0.44 | -0.58 |
| FR 2s10s steepener | momentum | 0.47 | 0.20 | -0.07 |
| FR 2s10s steepener | static |  | -0.36 |  |
| FR 2s5s10s fly 50/50 (long belly) | carry | 0.56 | 0.13 | -0.29 |
| FR 2s5s10s fly 50/50 (long belly) | meanrev | 0.30 | 0.01 | -0.28 |
| FR 2s5s10s fly 50/50 (long belly) | momentum | -0.24 | -0.93 | -1.53 |
| FR 2s5s10s fly 50/50 (long belly) | static |  | -0.01 |  |
| FR 2s5s10s fly PCA-weighted (long belly) | carry | 0.57 | -0.06 | -0.65 |
| FR 2s5s10s fly PCA-weighted (long belly) | meanrev | 0.27 | -0.05 | -0.36 |
| FR 2s5s10s fly PCA-weighted (long belly) | momentum | -0.26 | -1.01 | -1.66 |
| FR 2s5s10s fly PCA-weighted (long belly) | static |  | -0.29 |  |
| FR 5s30s steepener | carry | 0.32 | 0.09 | -0.14 |
| FR 5s30s steepener | meanrev | 0.02 | -0.17 | -0.35 |
| FR 5s30s steepener | momentum | 0.14 | -0.27 | -0.66 |
| FR 5s30s steepener | static |  | 0.11 |  |
| JP 2s10s steepener | carry | 0.74 | 0.35 | -0.04 |
| JP 2s10s steepener | meanrev | -0.12 | -0.36 | -0.60 |
| JP 2s10s steepener | momentum | 0.02 | -0.54 | -1.06 |
| JP 2s10s steepener | static |  | -0.13 |  |
| JP 2s5s10s fly 50/50 (long belly) | carry | 0.82 | -0.18 | -1.01 |
| JP 2s5s10s fly 50/50 (long belly) | meanrev | 0.43 | -0.16 | -0.69 |
| JP 2s5s10s fly 50/50 (long belly) | momentum | -0.35 | -1.58 | -2.38 |
| JP 2s5s10s fly 50/50 (long belly) | static |  | -0.18 |  |
| JP 2s5s10s fly PCA-weighted (long belly) | carry | 0.54 | -0.68 | -1.53 |
| JP 2s5s10s fly PCA-weighted (long belly) | meanrev | 0.22 | -0.57 | -1.18 |
| JP 2s5s10s fly PCA-weighted (long belly) | momentum | -0.36 | -1.91 | -2.71 |
| JP 2s5s10s fly PCA-weighted (long belly) | static |  | -0.90 |  |
| JP 5s30s steepener | carry | 0.45 | 0.04 | -0.35 |
| JP 5s30s steepener | meanrev | 0.02 | -0.33 | -0.66 |
| JP 5s30s steepener | momentum | 0.15 | -0.55 | -1.14 |
| JP 5s30s steepener | static |  | -0.16 |  |
| PL 2s10s steepener | carry | 0.16 | -1.08 | -1.85 |
| PL 2s10s steepener | meanrev | -0.16 | -0.90 | -1.41 |
| PL 2s10s steepener | momentum | -0.25 | -1.75 | -2.44 |
| PL 2s10s steepener | static |  | -0.47 |  |
| PL 2s5s steepener | carry | 0.23 | -1.26 | -1.98 |
| PL 2s5s steepener | meanrev | 0.34 | -0.89 | -1.59 |
| PL 2s5s steepener | momentum | -0.33 | -2.06 | -2.68 |
| PL 2s5s steepener | static |  | -0.77 |  |
| PL 2s5s10s fly 50/50 (long belly) | carry | 0.44 | -1.54 | -2.20 |
| PL 2s5s10s fly 50/50 (long belly) | meanrev | 0.85 | -1.21 | -1.95 |
| PL 2s5s10s fly 50/50 (long belly) | momentum | -0.79 | -3.26 | -3.74 |
| PL 2s5s10s fly 50/50 (long belly) | static |  | -1.21 |  |
| PL 2s5s10s fly PCA-weighted (long belly) | carry | 0.41 | -2.26 | -2.85 |
| PL 2s5s10s fly PCA-weighted (long belly) | meanrev | 0.75 | -1.34 | -2.00 |
| PL 2s5s10s fly PCA-weighted (long belly) | momentum | -0.81 | -3.49 | -3.90 |
| PL 2s5s10s fly PCA-weighted (long belly) | static |  | -1.37 |  |
| PL 5s10s steepener | carry | 0.45 | -0.96 | -1.78 |
| PL 5s10s steepener | meanrev | 0.10 | -0.90 | -1.51 |
| PL 5s10s steepener | momentum | -0.26 | -2.20 | -2.91 |
| PL 5s10s steepener | static |  | -0.63 |  |
| UK 10y OIS spread (long = buy gilt, pay fixed OIS) | carry | 0.18 | 0.03 | -0.13 |
| UK 10y OIS spread (long = buy gilt, pay fixed OIS) | meanrev | -0.00 | -0.19 | -0.38 |
| UK 10y OIS spread (long = buy gilt, pay fixed OIS) | momentum | -0.22 | -0.72 | -1.18 |
| UK 10y OIS spread (long = buy gilt, pay fixed OIS) | static |  | 0.03 |  |
| UK 10y breakeven (long linker, short gilt) | carry | 0.10 | -0.09 | -0.29 |
| UK 10y breakeven (long linker, short gilt) | meanrev | 0.07 | -0.13 | -0.33 |
| UK 10y breakeven (long linker, short gilt) | momentum | -0.22 | -0.71 | -1.15 |
| UK 10y breakeven (long linker, short gilt) | static |  | -0.53 |  |
| UK 2s10s steepener | carry | 0.32 | 0.16 | -0.00 |
| UK 2s10s steepener | meanrev | -0.14 | -0.25 | -0.35 |
| UK 2s10s steepener | momentum | 0.05 | -0.18 | -0.41 |
| UK 2s10s steepener | static |  | -0.11 |  |
| UK 2s5s10s fly 50/50 (long belly) | carry | 0.82 | 0.27 | -0.24 |
| UK 2s5s10s fly 50/50 (long belly) | meanrev | -0.16 | -0.56 | -0.92 |
| UK 2s5s10s fly 50/50 (long belly) | momentum | 0.06 | -0.81 | -1.50 |
| UK 2s5s10s fly 50/50 (long belly) | static |  | -0.06 |  |
| UK 2s5s10s fly PCA-weighted (long belly) | carry | 0.73 | 0.06 | -0.53 |
| UK 2s5s10s fly PCA-weighted (long belly) | meanrev | 0.05 | -0.44 | -0.86 |
| UK 2s5s10s fly PCA-weighted (long belly) | momentum | -0.17 | -1.18 | -1.90 |
| UK 2s5s10s fly PCA-weighted (long belly) | static |  | -0.26 |  |
| UK 5s30s steepener | carry | -0.21 | -0.41 | -0.61 |
| UK 5s30s steepener | meanrev | 0.25 | 0.10 | -0.05 |
| UK 5s30s steepener | momentum | -0.04 | -0.42 | -0.79 |
| UK 5s30s steepener | static |  | -0.39 |  |
| US 10y breakeven (long TIPS, short nominal) | carry | -0.17 | -0.49 | -0.79 |
| US 10y breakeven (long TIPS, short nominal) | meanrev | 0.31 | 0.08 | -0.15 |
| US 10y breakeven (long TIPS, short nominal) | momentum | 0.14 | -0.32 | -0.76 |
| US 10y breakeven (long TIPS, short nominal) | static |  | -0.13 |  |
| US 10y swap spread (long = buy UST, pay fixed) | carry | 0.20 | 0.13 | 0.05 |
| US 10y swap spread (long = buy UST, pay fixed) | meanrev | 0.35 | 0.28 | 0.21 |
| US 10y swap spread (long = buy UST, pay fixed) | momentum | -0.50 | -0.68 | -0.87 |
| US 10y swap spread (long = buy UST, pay fixed) | static |  | -0.19 |  |
| US 2s10s steepener | carry | 0.22 | 0.12 | 0.02 |
| US 2s10s steepener | meanrev | -0.40 | -0.47 | -0.53 |
| US 2s10s steepener | momentum | 0.20 | 0.05 | -0.10 |
| US 2s10s steepener | static |  | 0.29 |  |
| US 2s5s10s fly 50/50 (long belly) | carry | 0.56 | 0.22 | -0.12 |
| US 2s5s10s fly 50/50 (long belly) | meanrev | 0.24 | 0.04 | -0.15 |
| US 2s5s10s fly 50/50 (long belly) | momentum | -0.22 | -0.70 | -1.15 |
| US 2s5s10s fly 50/50 (long belly) | static |  | -0.09 |  |
| US 2s5s10s fly PCA-weighted (long belly) | carry | 0.55 | 0.17 | -0.21 |
| US 2s5s10s fly PCA-weighted (long belly) | meanrev | 0.25 | 0.00 | -0.25 |
| US 2s5s10s fly PCA-weighted (long belly) | momentum | -0.29 | -0.83 | -1.32 |
| US 2s5s10s fly PCA-weighted (long belly) | static |  | -0.30 |  |
| US 5s30s steepener | carry | 0.23 | 0.13 | 0.03 |
| US 5s30s steepener | meanrev | 0.07 | -0.03 | -0.13 |
| US 5s30s steepener | momentum | 0.12 | -0.09 | -0.28 |
| US 5s30s steepener | static |  | 0.24 |  |
| US Baa vs 20y Treasury (long credit, rates-hedged) | carry | 0.33 | 0.19 | 0.06 |
| US Baa vs 20y Treasury (long credit, rates-hedged) | meanrev | -0.28 | -0.43 | -0.58 |
| US Baa vs 20y Treasury (long credit, rates-hedged) | momentum | 0.86 | 0.54 | 0.22 |
| US Baa vs 20y Treasury (long credit, rates-hedged) | static |  | 0.19 |  |
| cross-country 10y carry/vol (long best, short worst) | carry |  | 0.19 |  |
| long FR 10y vs short DE 10y | carry | 0.17 | -0.05 | -0.26 |
| long FR 10y vs short DE 10y | meanrev | 0.21 | 0.08 | -0.05 |
| long FR 10y vs short DE 10y | momentum | -0.19 | -0.62 | -1.03 |
| long FR 10y vs short DE 10y | static |  | -0.14 |  |
| long JP 10y vs short US 10y | carry | 0.13 | 0.05 | -0.03 |
| long JP 10y vs short US 10y | meanrev | 0.12 | 0.05 | -0.03 |
| long JP 10y vs short US 10y | momentum | -0.27 | -0.44 | -0.61 |
| long JP 10y vs short US 10y | static |  | -0.14 |  |
| long PL 10y vs short DE 10y | carry | 0.14 | -0.14 | -0.41 |
| long PL 10y vs short DE 10y | meanrev | 0.13 | -0.07 | -0.27 |
| long PL 10y vs short DE 10y | momentum | -0.36 | -0.87 | -1.31 |
| long PL 10y vs short DE 10y | static |  | -0.19 |  |
| long PL 10y vs short FR 10y | carry | 0.17 | -0.14 | -0.45 |
| long PL 10y vs short FR 10y | meanrev | 0.20 | -0.03 | -0.25 |
| long PL 10y vs short FR 10y | momentum | -0.52 | -1.05 | -1.50 |
| long PL 10y vs short FR 10y | static |  | -0.20 |  |
| long UK 10y vs short DE 10y | carry | 0.37 | 0.26 | 0.14 |
| long UK 10y vs short DE 10y | meanrev | 0.25 | 0.16 | 0.06 |
| long UK 10y vs short DE 10y | momentum | -0.42 | -0.65 | -0.87 |
| long UK 10y vs short DE 10y | static |  | -0.20 |  |
| long US 10y vs short DE 10y | carry | 0.12 | 0.06 | -0.01 |
| long US 10y vs short DE 10y | meanrev | 0.10 | 0.04 | -0.02 |
| long US 10y vs short DE 10y | momentum | -0.27 | -0.40 | -0.53 |
| long US 10y vs short DE 10y | static |  | -0.07 |  |
