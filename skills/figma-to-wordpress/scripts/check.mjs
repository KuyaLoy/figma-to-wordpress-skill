#!/usr/bin/env node
// check.mjs: browser check of a Figma build at the designed widths plus an overflow sweep. Full result on disk,
// a short summary on screen. Needs Playwright in the project (or globally):
//   npm i -D playwright && npx playwright install chromium
//
//   node check.mjs --base http://example.test --route / [--route /about/] [--page home] [--section hero]
//   node check.mjs --base http://example.test --progress _figma/progress.json      (every page's route)
//   options: --spec-dir _figma/spec  --out _figma/qa  --widths 1440,375  --sweep 320,768,1024,1280,1920
//            --tol 1440:1,375:2  --no-shots
//
// Sections are found by data-section="<slug>" on each section's root element. A spec file
// <spec-dir>/<page>--<section>.md with lines like "box@1440: w=1440 h=760" gives the Figma box per width.
// Exit code: 0 no issues, 1 issues found, 2 the check could not run.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

function parseArgs(argv) {
  const a = { route: [], widths: '1440,375', sweep: '320,768,1024,1280,1920', tol: '1440:1,375:2',
    out: '_figma/qa', specDir: '_figma/spec', shots: true };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    const v = () => argv[++i];
    if (k === '--base') a.base = v();
    else if (k === '--route') a.route.push(unmangle(v()));
    else if (k === '--page') a.page = v();
    else if (k === '--section') a.section = v();
    else if (k === '--progress') a.progress = v();
    else if (k === '--spec-dir') a.specDir = v();
    else if (k === '--out') a.out = v();
    else if (k === '--widths') a.widths = v();
    else if (k === '--sweep') a.sweep = v();
    else if (k === '--tol') a.tol = v();
    else if (k === '--no-shots') a.shots = false;
    else if (k === '--help' || k === '-h') a.help = true;
    else throw new Error(`unknown option ${k}`);
  }
  return a;
}

// Git Bash turns a route like "/about/" into "C:/Program Files/Git/about/": take it back.
export function unmangle(route) {
  const m = /^[A-Za-z]:[\\/].*?[\\/]Git([\\/].*)$/.exec(route);
  return m ? m[1].replace(/\\/g, '/') : route;
}

const nums = (s) => String(s || '').split(',').map((x) => parseInt(x, 10)).filter((n) => n > 0);

export function parseSpec(text) {
  const boxes = {};
  const re = /box@(\d+)\s*:\s*w\s*=\s*(\d+(?:\.\d+)?)\s*h\s*=\s*(\d+(?:\.\d+)?)/gi;
  let m;
  while ((m = re.exec(text))) boxes[m[1]] = { w: parseFloat(m[2]), h: parseFloat(m[3]) };
  return boxes;
}

function targets(a) {
  if (a.progress) {
    const data = JSON.parse(fs.readFileSync(a.progress, 'utf8'));
    return data.pages.filter((p) => p.route).map((p) => ({ route: p.route, page: p.slug }));
  }
  return a.route.map((r) => ({ route: r, page: a.page || '' }));
}

async function loadPlaywright() {
  try { return await import('playwright'); } catch { /* try the project */ }
  try { return createRequire(path.join(process.cwd(), 'noop.js'))('playwright'); } catch { return null; }
}

// Runs inside the page.
function inspect({ dpr, section }) {
  const vw = window.innerWidth;
  const out = { overflow: [], h1: 0, images: [], meta: {}, figmaUrls: [], lazyAboveFold: [], sections: {} };
  const doc = document.documentElement;
  if (doc.scrollWidth > vw + 1) {
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect();
      if (r.width && r.right > vw + 1 && getComputedStyle(el).position !== 'fixed') {
        const id = el.id ? `#${el.id}` : '';
        const cls = typeof el.className === 'string' && el.className ? `.${el.className.trim().split(/\s+/)[0]}` : '';
        out.overflow.push(`${el.tagName.toLowerCase()}${id}${cls} right=${Math.round(r.right)}`);
        if (out.overflow.length >= 5) break;
      }
    }
    if (!out.overflow.length) out.overflow.push(`page scrollWidth ${doc.scrollWidth} > ${vw}`);
  }
  out.h1 = document.querySelectorAll('h1').length;
  for (const img of document.images) {
    const r = img.getBoundingClientRect();
    const src = img.currentSrc || img.src || '';
    const name = src.split('/').pop().split('?')[0].slice(0, 60);
    if (!img.hasAttribute('alt')) out.images.push(`no alt: ${name}`);
    if (img.complete && img.naturalWidth === 0 && src) out.images.push(`broken: ${name}`);
    else if (r.width >= 40 && img.naturalWidth && img.naturalWidth < r.width * dpr * 0.95 && !/\.svg/i.test(src)) {
      out.images.push(`soft at DPR ${dpr}: ${name} ${img.naturalWidth}px for ${Math.round(r.width)}px`);
    }
    if (r.top < window.innerHeight && r.bottom > 0 && img.loading === 'lazy') out.lazyAboveFold.push(name);
  }
  const html = document.documentElement.outerHTML;
  const fig = html.match(/https?:\/\/(?:www\.)?figma\.com\/api\/mcp\/asset[^"'\s)]*|https?:\/\/(?:localhost|127\.0\.0\.1):3845\/[^"'\s)]*/g);
  if (fig) out.figmaUrls = [...new Set(fig)].slice(0, 5);
  const q = (s) => document.querySelector(s);
  out.meta = {
    title: (document.title || '').trim(), description: q('meta[name="description"]')?.content || '',
    canonical: q('link[rel="canonical"]')?.href || '', lang: doc.lang || '',
  };
  const sel = section ? `[data-section="${CSS.escape(section)}"]` : '[data-section]';
  for (const el of document.querySelectorAll(sel)) {
    const r = el.getBoundingClientRect();
    out.sections[el.dataset.section] = { w: Math.round(r.width * 10) / 10, h: Math.round(r.height * 10) / 10 };
  }
  return out;
}

async function main() {
  let a;
  try { a = parseArgs(process.argv.slice(2)); } catch (e) { console.log(`ERROR: ${e.message}`); process.exit(2); }
  if (a.help || !a.base) { console.log('Usage: see the top of check.mjs (needs --base).'); process.exit(a.help ? 0 : 2); }
  const list = targets(a);
  if (!list.length) { console.log('ERROR: no routes (--route or --progress)'); process.exit(2); }
  const pw = await loadPlaywright();
  if (!pw) { console.log('ERROR: Playwright not found. npm i -D playwright && npx playwright install chromium'); process.exit(2); }
  const widths = nums(a.widths);
  const sweep = nums(a.sweep).filter((w) => !widths.includes(w));
  const tol = Object.fromEntries(a.tol.split(',').map((x) => x.split(':').map(Number)));
  fs.mkdirSync(path.join(a.out, 'shots'), { recursive: true });
  let browser;
  try {
    browser = await pw.chromium.launch();
  } catch {
    try { browser = await pw.chromium.launch({ channel: 'chrome' }); } catch {
      console.log('ERROR: no browser for Playwright: npx playwright install chromium');
      process.exit(2);
    }
  }
  const result = { base: a.base, at: new Date().toISOString(), routes: [] };
  let issues = 0;
  const lines = [];
  for (const t of list) {
    const url = new URL(t.route, a.base).href;
    const rr = { route: t.route, page: t.page, widths: {} };
    for (const w of [...widths, ...sweep]) {
      const designed = widths.includes(w);
      const ctx = await browser.newContext({ viewport: { width: w, height: designed && w < 768 ? 812 : 900 },
        deviceScaleFactor: 2 });
      const page = await ctx.newPage();
      const errors = [];
      page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text().slice(0, 160)); });
      page.on('pageerror', (e) => errors.push(String(e.message).slice(0, 160)));
      const found = [];
      let res = null;
      try {
        res = await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
      } catch (e) {
        found.push(`load failed: ${e.message.split('\n')[0]}`);
      }
      if (res) {
        if (res.status() >= 400) found.push(`HTTP ${res.status()}`);
        const r = await page.evaluate(inspect, { dpr: 2, section: a.section || '' });
        for (const o of r.overflow) found.push(`overflow: ${o}`);
        if (designed) {
          if (!a.section && r.h1 !== 1) found.push(`h1 count ${r.h1} (want 1)`);
          for (const i of r.images) found.push(`image ${i}`);
          for (const l of r.lazyAboveFold) found.push(`lazy above the fold: ${l}`);
          for (const f of r.figmaUrls) found.push(`temporary Figma asset URL: ${f}`);
          if (!a.section) {
            if (!r.meta.title) found.push('no <title>');
            if (!r.meta.description) found.push('no meta description');
            if (!r.meta.canonical) found.push('no canonical');
            if (!r.meta.lang) found.push('no <html lang>');
          }
          for (const e of errors) found.push(`console: ${e}`);
          for (const [slug, box] of Object.entries(r.sections)) {
            const spec = t.page ? path.join(a.specDir, `${t.page}--${slug}.md`) : '';
            if (!spec || !fs.existsSync(spec)) continue;
            const want = parseSpec(fs.readFileSync(spec, 'utf8'))[w];
            if (!want) continue;
            const tl = tol[w] ?? 1;
            const dh = Math.round((box.h - want.h) * 10) / 10;
            const dw = Math.round((box.w - want.w) * 10) / 10;
            if (Math.abs(dh) > tl || Math.abs(dw) > tl) {
              found.push(`section ${slug}: ${box.w}x${box.h}, Figma ${want.w}x${want.h} (dw ${dw}, dh ${dh}, tol ${tl})`);
            }
          }
          if (a.section && !Object.keys(r.sections).length) found.push(`no element with data-section="${a.section}"`);
          if (a.shots) {
            const name = `${(t.page || t.route.replace(/[^a-z0-9]+/gi, '-')).replace(/^-|-$/g, '') || 'home'}-${w}.jpg`;
            const target = a.section ? page.locator(`[data-section="${a.section}"]`).first() : page;
            try {
              await target.screenshot({ path: path.join(a.out, 'shots', name), type: 'jpeg', quality: 70,
                ...(a.section ? {} : { fullPage: true }) });
            } catch { /* a missing section is already a finding */ }
          }
        }
      }
      rr.widths[w] = { designed, issues: found };
      issues += found.length;
      if (found.length) lines.push(`${t.route} @${w}: ${found.length} issue(s): ${found.slice(0, 4).join(' | ')}${found.length > 4 ? ' | ...' : ''}`);
      await ctx.close();
    }
    result.routes.push(rr);
  }
  await browser.close();
  const stamp = result.at.replace(/[:.]/g, '-').slice(0, 19);
  const file = path.join(a.out, `check-${stamp}.json`);
  fs.writeFileSync(file, JSON.stringify(result, null, 1));
  console.log(`${issues ? 'ISSUES' : 'PASS'}: ${list.length} route(s), widths ${widths.join('/')} + sweep ${sweep.join('/') || 'none'}, ${issues} issue(s). Full: ${file}`);
  for (const l of lines.slice(0, 30)) console.log(`- ${l}`);
  if (lines.length > 30) console.log(`- ... ${lines.length - 30} more lines in the file`);
  process.exit(issues ? 1 : 0);
}

if (import.meta.url === `file://${process.argv[1]}` || process.argv[1]?.endsWith('check.mjs')) main();
