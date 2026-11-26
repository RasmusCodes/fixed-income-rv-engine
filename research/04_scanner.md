# Relative-value scanner snapshot (2026-11-20)

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

| market | trade | level_bp | z_1y | z_3y | pct_5y | carry_roll_3m | vol_ann_bp | carry_to_vol | half_life_w |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FR-DE | FR 30y vs DE 30y (long FR) | -165.96 | -2.54 | -3.87 | 0.77 | 3.26 | 57.64 | 0.23 | 30.15 |
| FR-DE | FR 10y vs DE 10y (long FR) | -145.39 | -2.51 | -4.07 | 0.77 | 6.32 | 58.82 | 0.43 | 132.46 |
| US | US 10y breakeven (long TIPS) | 215.00 | -2.45 | -1.87 | 3.07 | 3.34 | 32.01 | 0.42 | 3.54 |
| FR | FR 2s5s10s fly, long belly (50/50) | 2.00 | -2.41 | -1.85 | 10.73 | -1.88 | 17.59 | -0.43 | 17.10 |
| PL | PL 2s5s steepener | 103.16 | 2.33 | 2.09 | 99.62 | 10.23 | 42.43 | 0.96 | 29.05 |
| PL | PL 2s5s10s fly, long belly (50/50) | -23.43 | -2.32 | -2.61 | 4.00 | -1.10 | 22.16 | -0.20 | 9.46 |
| UK | UK 5s30s steepener | 73.29 | -2.31 | -0.75 | 57.09 | 3.89 | 42.27 | 0.37 | 27.24 |
| UK | UK 10s30s steepener | 41.56 | -2.20 | -1.32 | 43.30 | 2.79 | 23.03 | 0.48 | 16.78 |
| FR-DE | FR 2y vs DE 2y (long FR) | -50.97 | -2.11 | -3.30 | 1.15 | 10.97 | 51.95 | 0.84 | 6.84 |
| FR | FR 5s10s30s fly, long belly (50/50) | -4.35 | -1.98 | -2.08 | 7.28 | 0.52 | 15.68 | 0.13 | 21.46 |
| PL-FR | PL 2y vs FR 2y (long PL) | -100.55 | 1.98 | 2.05 | 99.62 | 6.37 | 87.99 | 0.29 | 63.17 |
| UK | UK 2s5s10s fly, long belly (50/50) | 5.47 | -1.97 | -2.10 | 8.81 | -4.55 | 7.50 | -2.42 | 48.72 |
| UK | UK 2s10s steepener | 52.51 | -1.82 | 0.24 | 65.90 | 11.28 | 44.01 | 1.03 | 44.14 |
| FR | FR 10s30s steepener | 55.20 | -1.81 | -0.61 | 55.56 | 5.15 | 31.65 | 0.65 | 26.02 |
| PL-FR | PL 10y vs FR 10y (long PL) | -136.21 | 1.74 | 1.97 | 98.80 | 0.09 | 85.30 | 0.00 | 22.07 |

## PCA rich/cheap by tenor

Today's yield minus its fit from three principal components of two years of yield levels
(positive = the point is cheap relative to the curve's usual shape):

| market | tenor | yield_pct | pca_resid_bp | resid_z | asof |
|---|---:|---:|---:|---:|---|
| FR | 2.00 | 3.64 | -2.71 | -2.02 | 2026-11-20 |
| FR | 20.00 | 5.33 | 1.16 | 1.98 | 2026-11-20 |
| JP | 3.00 | 1.95 | -2.63 | -1.86 | 2026-11-19 |
| JP | 1.00 | 1.66 | 3.71 | 1.77 | 2026-11-19 |
| FR | 10.00 | 4.87 | -1.30 | -1.57 | 2026-11-20 |
| US | 30.00 | 5.31 | 1.94 | 1.55 | 2026-11-20 |
| FR | 1.00 | 3.37 | 2.49 | 1.48 | 2026-11-20 |
| US | 10.00 | 4.92 | -2.61 | -1.31 | 2026-11-20 |
| JP | 10.00 | 2.87 | 1.69 | 1.31 | 2026-11-19 |
| JP | 30.00 | 4.03 | -1.84 | -1.20 | 2026-11-19 |

Full table (48 rows): [generated/04_scanner.md](generated/04_scanner.md).
