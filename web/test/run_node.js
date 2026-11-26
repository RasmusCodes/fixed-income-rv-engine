// Run the firv.js parity checks in Node (no browser): node web/test/run_node.js
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ctx = { console, Math, Number, Array, Object, Set, Map, JSON, Error, isFinite, isNaN };
ctx.globalThis = ctx;
ctx.window = ctx;
vm.createContext(ctx);
for (const f of ['../firv.js', 'golden.js', 'checks.js']) {
  vm.runInContext(fs.readFileSync(path.join(__dirname, f), 'utf8'), ctx, { filename: f });
}
const rows = ctx.runChecks(ctx.FIRV, ctx.GOLDEN);
const bad = rows.filter((r) => !r.ok);
for (const r of bad) console.log(`FAIL ${r.name}: diff ${r.diff} > tol ${r.tol}`);
console.log(`SELFTEST ${bad.length ? 'FAIL' : 'PASS'} ${rows.length - bad.length}/${rows.length}`);
process.exit(bad.length ? 1 : 0);
