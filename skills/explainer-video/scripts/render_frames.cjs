#!/usr/bin/env node
/* Render a film page frame by frame, or a few stills.

   node render_frames.cjs <page.html> <out_dir> --stills 1.5,6,12     one JPEG per time
   node render_frames.cjs <page.html> <out_dir> --fps 30              every frame: f00000.jpg ...
   Options: --size 1080x1920 (default), --quality 92

   The page must set window.FILM = {ready, END, SEEK(t), SFX} once it has loaded (see
   assets/starter.html). The page's folder is served over http so fonts and fetches work.
   Writes <out_dir>/sfx.json (the page's logged sound events) and, if the page sets FILM.STROKES,
   <out_dir>/strokes.json (pen-down intervals, for a synthesised scratch). Stops on page errors.
   Playwright is resolved from the current folder, then from $PLAYWRIGHT_PATH. */
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const args = process.argv.slice(2);
if (args.length < 2) { console.error('usage: render_frames.cjs <page.html> <out_dir> (--stills t1,t2 | --fps 30)'); process.exit(2); }
const opt = (k, d) => { const i = args.indexOf(k); return i > -1 ? args[i + 1] : d; };
let playwright;
try { playwright = require(require.resolve('playwright', {paths: [process.cwd()]})); }
catch { playwright = require(process.env.PLAYWRIGHT_PATH || 'playwright'); }
const page = path.resolve(args[0]), out = path.resolve(args[1]), root = path.dirname(page);
const [W, H] = opt('--size', '1080x1920').split('x').map(Number), quality = +opt('--quality', 92);
const types = {'.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.woff': 'font/woff', '.css': 'text/css'};
// Serve the page's folder and its parent, so ../node_modules works.
const base = path.dirname(root);
const srv = http.createServer((q, r) => {
  const f = path.join(base, decodeURIComponent(q.url.split('?')[0]));
  if (f !== base && !f.startsWith(base + path.sep)) { r.writeHead(403); return r.end(); }
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, {'content-type': types[path.extname(f)] || 'application/octet-stream'}); r.end(b); });
}).listen(0, '127.0.0.1');
(async () => {
  fs.mkdirSync(out, {recursive: true});
  const b = await playwright.chromium.launch(); const p = await b.newPage({viewport: {width: W, height: H}});
  const errors = []; p.on('pageerror', e => errors.push(e.message)); p.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  const url = `http://127.0.0.1:${srv.address().port}/${path.relative(base, page).split(path.sep).join('/')}`;
  await p.goto(url); await p.waitForFunction('window.FILM && window.FILM.ready', {timeout: 120000});
  if (errors.length) { console.error('page errors:\n' + errors.join('\n')); process.exitCode = 1; }
  fs.writeFileSync(path.join(out, 'sfx.json'), JSON.stringify(await p.evaluate('window.FILM.SFX || []')));
  const strokes = await p.evaluate('window.FILM.STROKES || null');
  if (strokes) fs.writeFileSync(path.join(out, 'strokes.json'), JSON.stringify(strokes));
  const shot = (file) => p.screenshot({path: path.join(out, file), type: 'jpeg', quality, clip: {x: 0, y: 0, width: W, height: H}});
  if (args.includes('--stills')) {
    for (const t of opt('--stills', '0').split(',')) { await p.evaluate(t => window.FILM.SEEK(t), +t); await shot(`s_${t}.jpg`); }
    if (errors.length) { console.error('page errors:\n' + errors.join('\n')); process.exitCode = 1; }
  } else {
    const fps = +opt('--fps', 30), END = await p.evaluate('window.FILM.END'), n = Math.round(END * fps);
    for (let i = 0; i < n; i++) {
      await p.evaluate(t => window.FILM.SEEK(t), i / fps); await shot(`f${String(i).padStart(5, '0')}.jpg`);
      if (errors.length) throw new Error('page error while rendering frame ' + i + ':\n' + errors.join('\n'));
      if (i % 300 === 0) console.log(`${i} / ${n}`);
    }
    console.log(`${n} frames at ${fps} fps -> ${out}`);
  }
  await b.close(); srv.close();
})().catch(e => { console.error(e); process.exit(1); });
