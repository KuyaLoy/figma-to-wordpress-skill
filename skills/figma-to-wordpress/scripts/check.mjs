#!/usr/bin/env node
// check.mjs: numeric check of a Figma build at the designed widths plus an overflow sweep. Full result on disk,
// a short summary on screen. Needs Playwright in the project (or globally); pixel diffs also need pixelmatch and pngjs:
//   npm i -D playwright pixelmatch pngjs && npx playwright install chromium
//
//   node check.mjs --base http://example.test --route / [--route /about/] [--page home] [--section hero]
//   node check.mjs --base http://example.test --progress _figma/progress.json      (every page's route)
//   options: --spec-dir _figma/spec  --out _figma/qa  --widths 1440,375  --sweep 320,768,1024,1280,1920
//            --tol 1440:1,375:2  --max-diff 0.02  --marks size=0.5,line=1,tracking=0.1,color=3,opacity=0.02
//            --settle 400  --no-shots  --no-pixel  --no-states
//
// Sections are found by data-section="<slug>" on each section's root element. The spec file
// <spec-dir>/<page>--<section>.md holds the Figma values, one per line (see references/qa.md):
//   box@1440: w=1440 h=760
//   el@1440: "Our services" font=Inter size=40 weight=600 line=48 tracking=-0.8 color=#15202b
//   el@375: img.hero-photo w=343 h=257 fit=cover pos="50% 30%"
//   state@1440: hover .btn-primary bg=#c2321f color=#ffffff
//   state@375: click .menu-toggle => .mobile-menu visible=1
// A Figma render <out>/figma/<page>--<section>@<width>.png (1x) turns on the pixel diff for that section and width;
// failing diffs are kept in <out>/diff/. Exit code: 0 no issues, 1 issues found, 2 the check could not run.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

export const MARKS = { size: 0.5, line: 1, tracking: 0.1, color: 3, opacity: 0.02, radius: 0.5 };

function parseArgs(argv) {
  const a = { route: [], widths: '1440,375', sweep: '320,768,1024,1280,1920', tol: '1440:1,375:2',
    out: '_figma/qa', specDir: '_figma/spec', shots: true, pixel: true, states: true, maxDiff: 0.02,
    marks: '', settle: 400 };
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
    else if (k === '--max-diff') a.maxDiff = parseFloat(v());
    else if (k === '--marks') a.marks = v();
    else if (k === '--settle') a.settle = parseInt(v(), 10);
    else if (k === '--no-shots') a.shots = false;
    else if (k === '--no-pixel') a.pixel = false;
    else if (k === '--no-states') a.states = false;
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

// key=value pairs; a value with spaces is quoted: pos="50% 30%".
export function parseProps(s) {
  const props = {};
  const re = /([a-z]+)=(?:"([^"]*)"|(\S+))/gi;
  let m;
  while ((m = re.exec(s))) props[m[1].toLowerCase()] = m[2] ?? m[3];
  return props;
}

// A target is "quoted text" (an element whose text starts with it) or a CSS selector, inside the section.
function parseTarget(s) {
  const t = s.trim();
  const q = /^"([^"]*)"$/.exec(t);
  return q ? { text: q[1] } : { css: t };
}

// Splits "<target part> key=value ..." where props start at the first " key=" outside brackets and quotes.
function splitProps(rest) {
  let depth = 0;
  let inQ = false;
  for (let i = 0; i < rest.length; i++) {
    const c = rest[i];
    if (c === '"') inQ = !inQ;
    else if (!inQ && c === '[') depth++;
    else if (!inQ && c === ']') depth--;
    else if (!inQ && depth === 0 && /\s/.test(c) && /^\s+[a-z]+=/i.test(rest.slice(i)) && !/^\s+=>/.test(rest.slice(i))) {
      return [rest.slice(0, i).trim(), rest.slice(i).trim()];
    }
  }
  return [rest.trim(), ''];
}

export function parseSpec(text) {
  const spec = { box: {}, el: {}, state: {} };
  for (const raw of String(text).split(/\r?\n/)) {
    const line = raw.replace(/^\s*(?:[-*]\s+)?`?/, '').replace(/`\s*$/, '');
    let m = /^box@(\d+)\s*:\s*w\s*=\s*(\d+(?:\.\d+)?)\s*h\s*=\s*(\d+(?:\.\d+)?)/i.exec(line);
    if (m) { spec.box[m[1]] = { w: parseFloat(m[2]), h: parseFloat(m[3]) }; continue; }
    m = /^el@(\d+)\s*:\s*(.+)$/i.exec(line);
    if (m) {
      const [target, props] = splitProps(m[2]);
      (spec.el[m[1]] ||= []).push({ target: parseTarget(target), props: parseProps(props), line: line.trim() });
      continue;
    }
    m = /^state@(\d+)\s*:\s*(hover|focus|click|swipe)\s+(.+)$/i.exec(line);
    if (m) {
      const [targets, props] = splitProps(m[3]);
      const [on, check] = targets.split(/\s+=>\s+/);
      spec.state[m[1]] ||= [];
      spec.state[m[1]].push({ action: m[2].toLowerCase(), on: parseTarget(on), check: parseTarget(check || on),
        props: parseProps(props), line: line.trim() });
    }
  }
  return spec;
}

export function hexToRgba(hex) {
  let h = String(hex).trim().replace(/^#/, '');
  if (h.length === 3 || h.length === 4) h = [...h].map((c) => c + c).join('');
  if (!/^[0-9a-f]{6}([0-9a-f]{2})?$/i.test(h)) return null;
  const n = (i) => parseInt(h.slice(i, i + 2), 16);
  return [n(0), n(2), n(4), h.length === 8 ? Math.round((n(6) / 255) * 100) / 100 : 1];
}

const POS = { left: '0%', top: '0%', center: '50%', right: '100%', bottom: '100%' };
const normPos = (s) => {
  const p = String(s).trim().toLowerCase().split(/\s+/).map((x) => POS[x] || x);
  if (p.length === 1) p.push('50%');
  return p.join(' ');
};
const squash = (s) => String(s).toLowerCase().replace(/["'_\-\s]/g, '');

// Compares one element's measured values with the spec's. Returns a list of differences ("" when it passes).
export function compareProps(want, got, marks, boxTol) {
  const out = [];
  const num = (k, tol, unit = 'px') => {
    if (want[k] === undefined) return;
    const w = parseFloat(want[k]);
    const g = got[k];
    if (g === null || g === undefined || Number.isNaN(g)) out.push(`${k} ${got[k]} (Figma ${w})`);
    else if (Math.abs(g - w) > tol + 1e-9) out.push(`${k} ${Math.round(g * 100) / 100}${unit} (Figma ${w}${unit})`);
  };
  num('size', marks.size);
  num('line', marks.line);
  num('tracking', marks.tracking);
  num('w', boxTol);
  num('h', boxTol);
  num('radius', marks.radius);
  num('opacity', marks.opacity, '');
  if (want.weight !== undefined && Number(got.weight) !== Number(want.weight)) out.push(`weight ${got.weight} (Figma ${want.weight})`);
  if (want.font !== undefined && !squash(got.font).includes(squash(want.font))) out.push(`font ${got.font} (Figma ${want.font})`);
  for (const k of ['color', 'bg']) {
    if (want[k] === undefined) continue;
    const w = hexToRgba(want[k]);
    const g = got[k];
    if (!w) { out.push(`${k}: bad value in spec "${want[k]}"`); continue; }
    if (!g || w.slice(0, 3).some((c, i) => Math.abs(c - g[i]) > marks.color) || Math.abs(w[3] - g[3]) > 0.02) {
      out.push(`${k} ${g ? `rgba(${g.join(',')})` : 'none'} (Figma ${want[k]})`);
    }
  }
  if (want.fit !== undefined && got.fit !== want.fit) out.push(`object-fit ${got.fit} (Figma ${want.fit})`);
  if (want.pos !== undefined && normPos(got.pos) !== normPos(want.pos)) out.push(`object-position ${got.pos} (Figma ${want.pos})`);
  if (want.visible !== undefined && Number(want.visible) !== (got.visible ? 1 : 0)) out.push(`visible ${got.visible ? 1 : 0} (want ${want.visible})`);
  if (want.focusring !== undefined && Number(want.focusring) !== (got.focusring ? 1 : 0)) out.push(`focus ring ${got.focusring ? 1 : 0} (want ${want.focusring})`);
  return out;
}

function targets(a) {
  if (a.progress) {
    const data = JSON.parse(fs.readFileSync(a.progress, 'utf8'));
    return data.pages.filter((p) => p.route).map((p) => ({ route: p.route, page: p.slug }));
  }
  return a.route.map((r) => ({ route: r, page: a.page || '' }));
}

// From this script's own folder first, then from the project the check runs in (CommonJS or ES module).
async function loadModule(name) {
  let m = null;
  try { m = await import(name); } catch { /* try the project */ }
  if (!m) {
    try {
      const file = createRequire(path.join(process.cwd(), 'noop.js')).resolve(name);
      m = await import(pathToFileURL(file).href);
    } catch { return null; }
  }
  return m.default ?? m; // a CommonJS package arrives as its default export
}

// Runs inside the page: page-wide checks.
function inspect({ dpr, section }) {
  const vw = window.innerWidth;
  const out = { overflow: [], clipped: [], h1: 0, images: [], meta: {}, figmaUrls: [], lazyAboveFold: [], sections: {} };
  const doc = document.documentElement;
  const label = (el) => {
    const id = el.id ? `#${el.id}` : '';
    const cls = typeof el.className === 'string' && el.className.trim() ? `.${el.className.trim().split(/\s+/)[0]}` : '';
    const sec = el.closest('[data-section]');
    return `${sec ? `[${sec.dataset.section}] ` : ''}${el.tagName.toLowerCase()}${id}${cls}`;
  };
  if (doc.scrollWidth > vw + 1) {
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect();
      if (r.width && r.right > vw + 1 && getComputedStyle(el).position !== 'fixed') {
        out.overflow.push(`${label(el)} right=${Math.round(r.right)}`);
        if (out.overflow.length >= 5) break;
      }
    }
    if (!out.overflow.length) out.overflow.push(`page scrollWidth ${doc.scrollWidth} > ${vw}`);
  }
  // Text cut by its box: overflow hidden or clip, content larger than the box. Line clamps and ellipses are meant.
  for (const el of document.querySelectorAll('body *')) {
    if (out.clipped.length >= 5) break;
    const cs = getComputedStyle(el);
    const hid = (v) => v === 'hidden' || v === 'clip';
    if (!hid(cs.overflowX) && !hid(cs.overflowY)) continue;
    if (el.clientWidth <= 1 || el.clientHeight <= 1 || cs.visibility === 'hidden' || cs.display === 'none') continue;
    if ((cs.webkitLineClamp && cs.webkitLineClamp !== 'none') || cs.textOverflow === 'ellipsis') continue;
    const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    if (!own && !el.textContent.trim()) continue;
    const cutY = hid(cs.overflowY) && el.scrollHeight > el.clientHeight + 1;
    const cutX = own && hid(cs.overflowX) && el.scrollWidth > el.clientWidth + 1;
    if (cutY || cutX) {
      const by = [cutX && `${el.scrollWidth}>${el.clientWidth}w`, cutY && `${el.scrollHeight}>${el.clientHeight}h`].filter(Boolean);
      out.clipped.push(`${label(el)} ${by.join(' ')}`);
    }
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

// Runs inside the page: finds a target inside a section, marks it, and returns its measured values.
function measure({ section, target, mark }) {
  const root = document.querySelector(`[data-section="${CSS.escape(section)}"]`);
  if (!root) return { error: `no section ${section}` };
  let el = null;
  if (target.css) {
    try { el = root.matches(target.css) ? root : root.querySelector(target.css); } catch { return { error: `bad selector ${target.css}` }; }
  } else {
    const norm = (s) => s.replace(/\s+/g, ' ').trim();
    const want = norm(target.text);
    const hits = [...root.querySelectorAll('*')].filter((e) => norm(e.textContent).startsWith(want));
    el = hits.find((e) => ![...e.children].some((c) => norm(c.textContent).startsWith(want))) || null;
  }
  if (!el) return { error: `not found: ${target.css || `"${target.text}"`}` };
  if (mark) el.setAttribute('data-qa-target', mark);
  const cs = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  const rgba = (v) => {
    const m = /rgba?\(([^)]+)\)/.exec(v || '');
    if (!m) return null;
    const p = m[1].split(/[\s,/]+/).filter(Boolean).map(Number);
    return [p[0], p[1], p[2], p[3] ?? 1];
  };
  const px = (v) => (v === 'normal' ? null : parseFloat(v));
  const size = parseFloat(cs.fontSize);
  return {
    font: cs.fontFamily.split(',')[0].trim(), size, weight: Number(cs.fontWeight),
    line: cs.lineHeight === 'normal' ? null : px(cs.lineHeight), tracking: cs.letterSpacing === 'normal' ? 0 : px(cs.letterSpacing),
    color: rgba(cs.color), bg: rgba(cs.backgroundColor), w: Math.round(r.width * 10) / 10, h: Math.round(r.height * 10) / 10,
    fit: cs.objectFit, pos: cs.objectPosition, opacity: Number(cs.opacity), radius: parseFloat(cs.borderTopLeftRadius),
    visible: r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && Number(cs.opacity) > 0 && r.right > 0 && r.left < window.innerWidth,
    focusring: (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0) || (cs.boxShadow && cs.boxShadow !== 'none'),
  };
}

const STABLE_CSS = '*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}';

async function stabilise(page) {
  await page.addStyleTag({ content: STABLE_CSS });
  await page.evaluate(async () => {
    for (const img of document.images) if (img.loading === 'lazy') img.loading = 'eager';
    await Promise.all([...document.images].map((i) => (i.complete ? null : i.decode().catch(() => null))));
    if (document.fonts) await document.fonts.ready;
  });
}

function pixelDiff(lib, refFile, shot) {
  const { PNG } = lib.pngjs;
  const pixelmatch = lib.pixelmatch;
  const A = PNG.sync.read(fs.readFileSync(refFile));
  const B = PNG.sync.read(shot);
  const w = Math.max(A.width, B.width);
  const h = Math.max(A.height, B.height);
  const pad = (img) => {
    if (img.width === w && img.height === h) return img;
    const p = new PNG({ width: w, height: h, fill: true });
    p.data.fill(255);
    PNG.bitblt(img, p, 0, 0, img.width, img.height, 0, 0);
    return p;
  };
  const diff = new PNG({ width: w, height: h });
  const n = pixelmatch(pad(A).data, pad(B).data, diff.data, w, h, { threshold: 0.1 });
  return { share: n / (w * h), figma: `${A.width}x${A.height}`, site: `${B.width}x${B.height}`, png: PNG.sync.write(diff) };
}

async function main() {
  let a;
  try { a = parseArgs(process.argv.slice(2)); } catch (e) { console.log(`ERROR: ${e.message}`); process.exit(2); }
  if (a.help || !a.base) { console.log('Usage: see the top of check.mjs (needs --base).'); process.exit(a.help ? 0 : 2); }
  const list = targets(a);
  if (!list.length) { console.log('ERROR: no routes (--route or --progress)'); process.exit(2); }
  const pw = await loadModule('playwright');
  if (!pw) { console.log('ERROR: Playwright not found. npm i -D playwright && npx playwright install chromium'); process.exit(2); }
  const marks = { ...MARKS, ...Object.fromEntries(a.marks.split(',').filter(Boolean).map((x) => { const [k, v] = x.split('='); return [k, parseFloat(v)]; })) };
  const widths = nums(a.widths);
  const sweep = nums(a.sweep).filter((w) => !widths.includes(w));
  const tol = Object.fromEntries(a.tol.split(',').map((x) => x.split(':').map(Number)));
  const figDir = path.join(a.out, 'figma');
  const diffDir = path.join(a.out, 'diff');
  fs.mkdirSync(path.join(a.out, 'shots'), { recursive: true });
  let pix = null;
  let pixMissing = false;
  if (a.pixel && fs.existsSync(figDir) && fs.readdirSync(figDir).some((f) => f.endsWith('.png'))) {
    const pixelmatch = await loadModule('pixelmatch');
    const pngjs = await loadModule('pngjs');
    if (pixelmatch && pngjs) pix = { pixelmatch, pngjs }; else pixMissing = true;
  }
  let browser;
  try {
    browser = await pw.chromium.launch();
  } catch {
    try { browser = await pw.chromium.launch({ channel: 'chrome' }); } catch {
      console.log('ERROR: no browser for Playwright: npx playwright install chromium');
      process.exit(2);
    }
  }
  const specCache = {};
  const specFor = (pg, slug) => {
    const f = pg ? path.join(a.specDir, `${pg}--${slug}.md`) : '';
    if (!f || !fs.existsSync(f)) return null;
    return (specCache[f] ||= parseSpec(fs.readFileSync(f, 'utf8')));
  };
  const result = { base: a.base, at: new Date().toISOString(), marks, maxDiff: a.maxDiff, tol, routes: [] };
  let issues = 0;
  let pixelRuns = 0;
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
      const pixel = {};
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
        for (const c of r.clipped) found.push(`clipped text: ${c}`);
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
          if (a.section && !Object.keys(r.sections).length) found.push(`no element with data-section="${a.section}"`);
          const tl = tol[w] ?? 1;
          const withStates = [];
          for (const [slug, box] of Object.entries(r.sections)) {
            const spec = specFor(t.page, slug);
            if (!spec) continue;
            const want = spec.box[w];
            if (want) {
              const dh = Math.round((box.h - want.h) * 10) / 10;
              const dw = Math.round((box.w - want.w) * 10) / 10;
              if (Math.abs(dh) > tl || Math.abs(dw) > tl) {
                found.push(`section ${slug}: ${box.w}x${box.h}, Figma ${want.w}x${want.h} (dw ${dw}, dh ${dh}, tol ${tl})`);
              }
            }
            for (const el of spec.el[w] || []) {
              const got = await page.evaluate(measure, { section: slug, target: el.target, mark: '' });
              const diffs = got.error ? [got.error] : compareProps(el.props, got, marks, tl);
              if (diffs.length) found.push(`el ${slug} ${el.target.css || `"${el.target.text}"`}: ${diffs.join(', ')}`);
            }
            if (a.states && (spec.state[w] || []).length) withStates.push(slug);
          }
          if (pix || pixMissing) {
            const refs = Object.keys(r.sections).map((slug) => [slug, path.join(figDir, `${t.page}--${slug}@${w}.png`)])
              .filter(([, f]) => t.page && fs.existsSync(f));
            if (refs.length && pixMissing) found.push('pixel diff not run: npm i -D pixelmatch pngjs');
            if (refs.length && pix) {
              await stabilise(page);
              for (const [slug, ref] of refs) {
                pixelRuns++;
                const shot = await page.locator(`[data-section="${slug}"]`).first().screenshot({ scale: 'css', type: 'png' });
                const d = pixelDiff(pix, ref, shot);
                pixel[slug] = Math.round(d.share * 10000) / 100;
                if (d.share > a.maxDiff) {
                  fs.mkdirSync(diffDir, { recursive: true });
                  const base = path.join(diffDir, `${t.page}--${slug}@${w}`);
                  fs.writeFileSync(`${base}-diff.png`, d.png);
                  fs.writeFileSync(`${base}-site.png`, shot);
                  found.push(`pixel ${slug}: ${(d.share * 100).toFixed(2)}% differs (max ${(a.maxDiff * 100).toFixed(2)}%), Figma ${d.figma}, site ${d.site}, diff ${base}-diff.png`);
                }
              }
            }
          }
          for (const slug of withStates) {
            for (const st of specFor(t.page, slug).state[w]) {
              await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
              const on = await page.evaluate(measure, { section: slug, target: st.on, mark: 'on' });
              if (on.error) { found.push(`state ${slug} ${st.action}: ${on.error}`); continue; }
              const loc = page.locator('[data-qa-target="on"]').first();
              try {
                if (st.action === 'hover') await loc.hover();
                else if (st.action === 'focus') await loc.focus();
                else if (st.action === 'click') await loc.click();
                else {
                  const b = await loc.boundingBox();
                  const y = b.y + b.height / 2;
                  await page.mouse.move(b.x + b.width * 0.8, y);
                  await page.mouse.down();
                  await page.mouse.move(b.x + b.width * 0.2, y, { steps: 10 });
                  await page.mouse.up();
                }
              } catch (e) { found.push(`state ${slug} ${st.action}: ${e.message.split('\n')[0]}`); continue; }
              await page.waitForTimeout(a.settle);
              const got = await page.evaluate(measure, { section: slug, target: st.check, mark: '' });
              const diffs = got.error ? [got.error] : compareProps(st.props, got, marks, tl);
              if (diffs.length) found.push(`state ${slug} ${st.action} ${st.on.css || `"${st.on.text}"`}: ${diffs.join(', ')}`);
            }
          }
          if (a.shots) {
            const name = `${(t.page || t.route.replace(/[^a-z0-9]+/gi, '-')).replace(/^-|-$/g, '') || 'home'}${a.section ? `--${a.section}` : ''}-${w}.jpg`;
            if (withStates.length) await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
            const target = a.section ? page.locator(`[data-section="${a.section}"]`).first() : page;
            try {
              await target.screenshot({ path: path.join(a.out, 'shots', name), type: 'jpeg', quality: 70,
                ...(a.section ? {} : { fullPage: true }) });
            } catch { /* a missing section is already a finding */ }
          }
        }
      }
      rr.widths[w] = { designed, issues: found, pixel };
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
  console.log(`${issues ? 'ISSUES' : 'PASS'}: ${list.length} route(s), widths ${widths.join('/')} + sweep ${sweep.join('/') || 'none'}, ${pixelRuns} pixel diff(s), ${issues} issue(s). Full: ${file}`);
  for (const l of lines.slice(0, 30)) console.log(`- ${l}`);
  if (lines.length > 30) console.log(`- ... ${lines.length - 30} more lines in the file`);
  process.exit(issues ? 1 : 0);
}

// Run only as a script (a junction or symlink path ends the same way), never on import by the tests.
if (process.argv[1]?.replace(/\\/g, '/').endsWith('/check.mjs')) main();
