# Curve fitting: generated tables

Median over month ends (in-sample) and quarter ends (leave-one-out), bp of observed yields.

| market | in_sample cubic | in_sample ns | in_sample nss | in_sample spline | loo cubic | loo ns | loo nss | loo spline |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FR | 0.03 | 2.74 | 1.52 | 1.33 | 3.63 | 3.98 | 3.25 | 3.34 |
| JP | 0.02 | 3.54 | 2.23 | 1.38 | 2.62 | 4.60 | 3.73 | 3.14 |
| PL | 3.44 | 4.54 | 3.33 | 3.85 | 6.38 | 5.03 | 4.49 | 4.73 |
| US | 0.22 | 4.99 | 2.92 | 3.17 | 6.94 | 7.43 | 6.31 | 6.93 |

## Leave-one-out RMSE by regime (bp, median)

| market | regime | cubic | ns | nss | spline |
|---|---|---:|---:|---:|---:|
| FR | 2008-14 crisis and QE | 4.77 | 5.42 | 3.93 | 3.80 |
| FR | 2015-21 low and negative rates | 2.63 | 3.81 | 2.79 | 2.42 |
| FR | 2022-26 inflation and tightening | 4.10 | 4.19 | 3.33 | 3.95 |
| FR | pre-2008 | 2.44 | 2.28 | 2.62 | 1.99 |
| JP | 2008-14 crisis and QE | 2.29 | 5.16 | 3.62 | 2.70 |
| JP | 2015-21 low and negative rates | 1.68 | 2.94 | 2.12 | 1.90 |
| JP | 2022-26 inflation and tightening | 2.51 | 4.12 | 3.67 | 2.55 |
| JP | pre-2008 | 3.64 | 5.15 | 4.93 | 4.11 |
| PL | 2008-14 crisis and QE | 6.44 | 5.14 | 4.54 | 4.95 |
| PL | 2015-21 low and negative rates | 6.24 | 3.96 | 3.65 | 3.61 |
| PL | 2022-26 inflation and tightening | 7.85 | 5.64 | 5.14 | 5.75 |
| PL | pre-2008 | 5.47 | 8.20 | 7.88 | 8.09 |
| US | 2008-14 crisis and QE | 6.48 | 6.67 | 4.39 | 6.80 |
| US | 2015-21 low and negative rates | 4.16 | 4.55 | 4.23 | 4.55 |
| US | 2022-26 inflation and tightening | 9.92 | 8.49 | 6.49 | 8.92 |
| US | pre-2008 | 9.01 | 9.02 | 7.59 | 8.02 |

## Stability: excess day-to-day noise at unobserved tenors

Ratio of the noise of fitted changes around the interpolated neighbours' changes to the size of those changes (60 consecutive observations at the end of each regime; lower is steadier).

| market | regime | cubic | ns | nss | spline |
|---|---|---:|---:|---:|---:|
| FR | 2008-14 crisis and QE | 0.115 | 0.131 | 0.096 | 0.055 |
| FR | 2015-21 low and negative rates | 0.073 | 0.125 | 0.099 | 0.048 |
| FR | 2022-26 inflation and tightening | 0.075 | 0.086 | 0.057 | 0.034 |
| FR | pre-2008 | 0.047 | 0.079 | 0.063 | 0.037 |
| JP | 2008-14 crisis and QE | 0.117 | 0.082 | 0.081 | 0.062 |
| JP | 2015-21 low and negative rates | 0.338 | 0.202 | 0.378 | 0.175 |
| JP | 2022-26 inflation and tightening | 0.077 | 0.177 | 0.069 | 0.038 |
| JP | pre-2008 | 0.085 | 0.092 | 0.130 | 0.044 |
| US | 2008-14 crisis and QE | 0.081 | 0.091 | 0.074 | 0.048 |
| US | 2015-21 low and negative rates | 0.092 | 0.137 | 0.110 | 0.062 |
| US | 2022-26 inflation and tightening | 0.071 | 0.251 | 0.049 | 0.042 |
| US | pre-2008 | 0.057 | 0.180 | 0.123 | 0.050 |
