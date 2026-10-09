import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs';
// usage: node render.mjs data.js outdir fps [sampleTimes comma list]
const [,, dataPath, outdir, fpsArg, samples] = process.argv;
const fps = +fpsArg;
fs.mkdirSync(outdir, { recursive: true });
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on('pageerror', e => console.error('PAGE ERROR', e.message));
page.on('console', m => { if (m.type()==='error') console.error('CONSOLE', m.text()); });
await page.goto('file://' + new URL('engine.html', import.meta.url).pathname);
await page.evaluate(() => document.fonts.ready);
await page.addScriptTag({ path: dataPath });
const dur = await page.evaluate(() => window.__init(window.VIDEO));
console.log('duration', dur.toFixed(2), 's');
const t0 = Date.now();
if (samples) {
  for (const ts of samples.split(',')) { await page.evaluate(t => window.__setTime(t), +ts); await page.screenshot({ path: `${outdir}/t${ts}.png` }); }
} else {
  const n = Math.round(fps * dur);
  for (let i = 0; i < n; i++) { await page.evaluate(t => window.__setTime(t), i / fps); await page.screenshot({ path: `${outdir}/f${String(i).padStart(5,'0')}.png` }); }
  console.log('frames', n, 'ms/frame', ((Date.now()-t0)/n).toFixed(1));
}
await browser.close();
