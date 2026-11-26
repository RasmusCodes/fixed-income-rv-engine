/* Parity checks of firv.js against values produced by the Python engine (golden.js).
 * Used by selftest.html (browser) and run_node.js (Node, in CI). */
(function (root) {
  'use strict';
  root.runChecks = function (F, G) {
    const rows = [];
    function check(name, py, js, tol) {
      const pa = [].concat(py), ja = [].concat(js);
      let worst = 0;
      for (let i = 0; i < pa.length; i++) worst = Math.max(worst, Math.abs(pa[i] - ja[i]));
      const ok = isFinite(worst) && worst <= tol;
      rows.push({ name, py: pa.slice(0, 4), js: ja.slice(0, 4), diff: worst, tol, ok });
    }
    for (const [name, c] of Object.entries(G.fits)) {
      const data = { tenors: c.input.tenors, values: c.input.values.map((v) => v / 100), kind: c.input.kind, freq: c.input.freq };
      for (const [m, ref] of Object.entries(c.methods)) {
        let r;
        try { r = F.fit(m, data); } catch (e) { rows.push({ name: `${name} ${m}`, py: '', js: String(e), diff: NaN, tol: 0, ok: false }); continue; }
        // exact methods and NS must match closely; NSS and the spline use a different optimiser
        const loose = m === 'nss' || m === 'spline';
        check(`${name} ${m}: fitted values (decimal)`, ref.fitted, r.fitted, loose ? 0.75e-4 : 0.05e-4);
        check(`${name} ${m}: zero rates on grid`, ref.zero_grid, [0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30].map((t) => r.curve.zero(t)), loose ? 1.5e-4 : 0.1e-4);
        check(`${name} ${m}: RMSE bp`, ref.rmse_bp, r.rmse, loose ? 0.5 : 0.02);
      }
    }
    const R = G.risk;
    const curves = { g: new F.Svensson(R.svensson) };
    const b = F.parBond(curves, 'g', 10, 2);
    check('par bond coupon', R.bond10.coupon, b.coupon, 1e-12);
    check('par bond yield DV01', R.bond10.yield_dv01, b.yieldDV01(curves), 1e-10);
    check('par bond zero DV01', R.bond10.zero_dv01, F.dv01([{ ins: b, notional: 1 }], curves), 1e-10);
    const st = F.curveTrade(curves, 'g', 2, 10, 10000, 'steepener', 2);
    check('steepener notionals', R.steepener.notionals, st.map((l) => l.notional), 1e-3);
    check('steepener zero DV01', R.steepener.dv01, F.dv01(st, curves), 1e-4);
    check('steepener key-rate DV01s', R.steepener.krd, F.keyRateDV01(st, curves).g, 1e-4);
    const cr = F.carryRoll(st, curves, 0.25);
    check('steepener carry+roll 3m', [R.steepener.carry_roll.total, R.steepener.carry_roll.carry, R.steepener.carry_roll.roll], [cr.total, cr.carry, cr.roll], 1e-3);
    const shock = { g: curves.g.keyRateBumped([2, 10], [0, 0.0010]) };
    check('steepener scenario P&L', R.steepener.scenario, F.scenarioPnL(st, curves, shock).pnl, 1e-3);
    check('steepener scenario P&L at 3m horizon', R.steepener.scenario_h, F.scenarioPnL(st, curves, shock, 0.25).pnl, 1e-3);
    const fly = F.butterfly(curves, 'g', [2, 10], 5, 10000, [0.5, 0.5], 'long_belly', 2);
    check('fly notionals', R.fly.notionals, fly.map((l) => l.notional), 1e-3);
    const boot = F.bootstrapPar(G.fits.us_par.input.tenors, G.fits.us_par.input.values.map((v) => v / 100), 2);
    check('bootstrap zeros', R.boot_zero, [0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30].map((t) => boot.zero(t)), 1e-10);
    return rows;
  };
})(typeof window !== 'undefined' ? window : globalThis);
