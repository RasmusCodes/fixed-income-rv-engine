# Methodology

## 1. Conventions

- Rates are decimals in code (0.045 = 4.5%) and percent in data files; times are in years.
- Zero rates are continuously compounded: `df(t) = exp(-z(t) t)`. Every published central
  bank curve used here is continuously compounded; this was checked in the data, not
  assumed (section 7).
- Par yields have the market's coupon frequency: semiannual for US Treasuries, gilts and
  JGBs, annual for Bunds, OATs and Polish bonds. Maturities of one coupon period or less are
  money-market (simple) yields, as for bills.
- **DV01** is the value gained when yields fall 1 bp. Two versions are kept apart:
  - *yield DV01*: per bp of the instrument's own yield to maturity (street convention,
    `dirty = sum CF_k / (1 + y/f)^(t_k f)`), or per bp of the par swap rate for swaps.
    Trades are sized with it, because spreads are quoted in yields;
  - *zero-curve DV01*: per bp parallel shift of continuously compounded zero rates. Key-rate
    DV01s, risk aggregation across legs and scenario P&L use the curve.
  For a bond the two differ by roughly the factor (1 + y/f). A "DV01-neutral" steepener is
  neutral in yield DV01, so its zero-curve DV01 is small but not zero.

## 2. Curve models

| Model | Zero rate z(t) | Notes |
|---|---|---|
| Nelson-Siegel | b0 + b1 L1(t/tau) + b2 L2(t/tau) | L1(x) = (1-e^-x)/x, L2 = L1 - e^-x |
| Svensson (NSS) | NS + b3 L2(t/tau2) | the parameterisation of the Fed (GSW), ECB and Bundesbank |
| Smoothing spline | (1/t) integral of f, with f a cubic B-spline | knots at 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30, 40 years; forward held flat beyond the last knot |
| Cubic spline | natural cubic spline through zero rates | exact at the inputs (bootstrapped zeros for par data) |
| Bootstrap | log-linear discount factors | par yields interpolated monotonically (PCHIP) onto coupon dates, discount factors solved one date at a time |

**Fitting.** `firv.curves.fit(method, data)` works for three kinds of observation:
continuously compounded zero rates, par yields (with their coupon frequency) and bonds
(cash flows plus dirty prices). Residuals are always in bp of the observed quantity: zero
rate, par yield or yield to maturity.

- NS/NSS: a grid search over tau (28 values from 0.15 to 12 years; for NSS, pairs with tau2
  at least two grid steps above tau1) with betas from linear least squares on approximate
  zero rates, then nonlinear least squares on the actual residuals (bounded trust region in
  Python, projected Levenberg-Marquardt in JavaScript). tau2 is parameterised as tau1 + gap.
- Bond fits minimise duration-weighted price errors, which are first-order yield errors.
  Reported residuals are exact yield-to-maturity differences.
- The smoothing spline minimises the sum of squared errors plus lambda times the integral of
  f''(t)^2, both in bp (lambda = 0.05 by default), the roughness penalty of the variable
  roughness penalty family the Bank of England uses (Anderson and Sleath 2001).
- NSS parameters are often poorly identified: when tau1 and tau2 are close, b2 and b3 offset
  each other. The fitted curve is unaffected. Official curves show the same: since 2000,
  Bundesbank and ECB taus are within 0.13 and 0.04 years of each other on 5% of days.

**Out-of-sample error.** Leave one out: drop each interior observation, refit, and predict
it. An interpolating spline has zero in-sample error by construction, so only the
leave-one-out error compares it fairly with the parametric models.

**Stability.** On 60 consecutive observations at the end of each regime, curves are refitted
independently every day; the day-to-day change of the fitted par yield at maturities that
are not observed is compared with the linear interpolation of the neighbouring observed
changes. The ratio of the noise around that interpolation to the size of the changes
("excess noise") measures how much movement a model adds that is not in the data.

## 3. PCA and historical decomposition

PCA is run on daily changes (weekly for Poland) of par yields at fixed tenors. Changes are
computed before incomplete rows are dropped, so no change spans a gap in the data (the US
30-year CMT was not published from February 2002 to February 2006; the Bank of England
curve extends beyond 25 years only from 2016). Signs are normalised: PC1 rises with yields,
PC2 with steepening, PC3 with the belly cheapening. Any curve move between two dates is
decomposed into the first three components plus a residual; scenario shocks of k standard
deviations use the loadings scaled by each component's volatility.

## 4. Instruments and risk

- **Bonds on a time grid** (`CMBond`): coupons every 1/f years back from maturity; a short
  first period accrues pro rata; accrued interest is the run part of the current coupon.
- **Swaps**: single-curve, floating leg at par; PV01 is the annuity.
- **Linkers**: priced on a real curve in real terms; breakeven DV01 = real-yield DV01 with
  nominal yields fixed.
- **Credit bonds**: priced at a z-spread over the government curve; spread DV01 equals the
  zero-curve DV01 of the bond.
- **Bond futures**: fair price = (forward dirty price of the CTD - accrued at delivery) /
  conversion factor, forward financed at the repo rate; conversion factors follow the
  exchange formula (price at a 6% yield with maturity rounded down to whole quarters, checked
  against an independent bond pricer in the tests); gross basis, carry, net basis and implied
  repo. No free futures settlement prices exist for scripts, so basis is analytics only.

**Carry and roll-down** over horizon h assume curves do not move (same yield at the same
time to maturity). Total = value of the aged instrument + coupons received - value today -
financing (dirty value x funding rate x h). Carry is the same calculation if the bond kept
its own yield to maturity; roll-down is the remainder. For swaps, carry = (fixed rate -
floating rate fixed today) x h and roll-down is the revaluation of the shorter swap.

**Scenario P&L** is full revaluation on shocked curves, instantly or at the horizon (carry
and roll-down first, then the shock applied to the aged trade). A DV01-neutral trade drifts
as it ages because legs lose DV01 at different speeds; the horizon column includes that.

**Comparing trades.** P&L volatility is the square root of k' Sigma k, with k the key-rate or
yield DV01 vector and Sigma the covariance of yield changes; carry and roll-down per year
divided by that volatility, and the breakeven yield move (carry over DV01), put trades of
different shapes on one scale.

## 5. Trade construction

All constructors take a target DV01 in money per bp:

- curve trades: steepener (long short tenor, short long tenor) or flattener, DV01-neutral or
  beta-weighted (short-tenor leg = beta x DV01, beta from regressing long-tenor on
  short-tenor yield changes);
- butterflies: belly vs wings, wings 50/50, from a regression of belly changes on wing
  changes, or PCA-neutral (wing weights that zero the fly's exposure to PC1 and PC2);
- factor trades: minimum-norm DV01 vector with exposure only to one principal component;
- cross-country spreads: DV01 in the long leg's currency, the hedge leg converted at the ECB
  reference rate and optionally scaled by a regression beta; each leg financed at its own
  short rate; the currency risk of the P&L itself is not hedged;
- swap spreads (bond vs swap), futures basis (bond vs CF-weighted futures), breakevens
  (linker vs nominal, optionally beta-weighted), credit (z-spread bond vs government bond).

## 6. Backtests

A strategy is a DV01-weighted set of constant-maturity legs (+1 = one unit of DV01 long).
Daily P&L of a leg held with position q, in bp per unit of DV01:

    q x ( -dy + 0.5 (C/D) dy^2 1e-4 + (carry + roll) x days )

with dy in bp, D and C the modified duration and convexity of a par bond at the leg's
yield, carry = (y - funding) / (365 D) and roll = curve slope at the tenor / 365 (bp per day).
Funding: SOFR (3-month bill before April 2018), EUR STR (6-month Bund zero rate before October
2019), Bank Rate, BoJ and NBP policy rates; linkers are financed in real terms (funding minus
CPI inflation, BIS series lagged one month).

Signals are computed at each weekly close from data up to that close and earn P&L from the
next observation: **mean reversion** (z-score of the trade's spread against its trailing
history; enter beyond `entry`, exit inside `exit` or on a sign change), **carry** (sign of
expected carry and roll-down), **momentum** (sign of the 13-week change, a control), and
**static** (always on).

**Costs.** Each position change pays the one-way cost per leg (half the bid/offer, bp of
yield); constant-maturity positions pay a round trip every three months to roll into the new
benchmark. One-way costs are assumptions for the US (0.20-0.40 bp), Germany (0.30-0.50),
France (0.40-0.70), the UK (0.30-0.60), Japan (0.50-0.80), swaps (0.20-0.40) and linkers
(1.0-1.5); for Poland they are measured from the BondSpot fixing's bid and offer yields over
the last three years (4.5 bp at 2 years, 2.5 bp at 5, 2.0 bp at 10). Every result is also
shown at 0x and 2x costs.

**Validation.** (1) Fixed default parameters (52-week lookback, entry 1.5, exit 0.25) over
the full sample; (2) parameters chosen on the first half from an 18-point grid and reported
on the second half; (3) walk-forward: parameters re-selected every year on all earlier data,
out-of-sample years concatenated. Means are tested with Newey-West t-statistics. 36
walk-forward tests are run, so a |t| near 2 is expected by chance about twice; only results
well beyond that should be read as evidence.

## 7. Data checks built into the pipeline

- Bundesbank, Fed (GSW) and ECB zero rates reproduce from their published Svensson
  parameters with the continuously compounded formula (median error 0.44 bp, 0.00 bp and
  0.00 bp; reading them as annually compounded misses by a median 4-17 bp).
- Bank of England spot rates are continuous: from September 2023 to April 2024, while Bank
  Rate was 5.25%, the one-month OIS spot averaged 5.1895%. Read as continuously compounded,
  that is an overnight rate of about 5.19%, a few basis points below Bank Rate; read as
  annually compounded, it would imply about 5.06%, implausibly far below it.
- Polish coupons are inferred from fixing price and yield (price is linear in the coupon at
  a fixed yield) and accepted only when the rounded coupon reproduces the published yields
  (median error 0.36 bp); two 2006-07 bonds that fail are excluded.
- The JavaScript engine is checked against the Python one on 53 values (fits, bootstrap,
  DV01s, notionals, key rates, carry and roll, scenarios).
