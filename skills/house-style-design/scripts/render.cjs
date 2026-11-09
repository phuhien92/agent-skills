#!/usr/bin/env node
/* Render every .card (or a chosen selector) in a design page to PNG at 2x, plus a contact sheet.

   node render.cjs <page.html> <out_dir> [--selector .card] [--scale 2]

   Writes <out_dir>/<id or index>.png for each match (transparent corners) and <out_dir>/sheet.png
   (the whole page). Fails on page or console errors, such as a missing font file.
   Playwright is resolved from the current folder, then from $PLAYWRIGHT_PATH. */
const fs = require('node:fs'), path = require('node:path');
const args = process.argv.slice(2);
if (args.length < 2) { console.error('usage: render.cjs <page.html> <out_dir> [--selector .card] [--scale 2]'); process.exit(2); }
const opt = (k, d) => { const i = args.indexOf(k); return i > -1 ? args[i + 1] : d; };
let playwright;
try { playwright = require(require.resolve('playwright', {paths: [process.cwd()]})); }
catch { playwright = require(process.env.PLAYWRIGHT_PATH || 'playwright'); }
(async () => {
  const page = path.resolve(args[0]), out = path.resolve(args[1]), sel = opt('--selector', '.card'), scale = +opt('--scale', 2);
  fs.mkdirSync(out, {recursive: true});
  const b = await playwright.chromium.launch();
  const p = await b.newPage({viewport: {width: 1800, height: 1200}, deviceScaleFactor: scale});
  const errors = []; p.on('pageerror', e => errors.push(e.message));
  p.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  p.on('requestfailed', r => errors.push('failed to load ' + r.url()));
  await p.goto('file://' + page); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  const sheetPath = path.join(out, 'sheet.png');
  await p.screenshot({path: sheetPath, fullPage: true});                       // contact sheet on the page's own background
  await p.addStyleTag({content: 'html,body{background:transparent!important}'}); // then cards with transparent corners
  const n = await p.locator(sel).count();
  for (let i = 0; i < n; i++) {
    const loc = p.locator(sel).nth(i), id = (await loc.getAttribute('id')) || String(i + 1);
    await loc.screenshot({path: path.join(out, `${id}.png`), omitBackground: true});
  }
  console.log(`${n} design(s) -> ${out}`);
  if (errors.length) { console.error('page errors:\n' + errors.join('\n')); process.exitCode = 1; }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
