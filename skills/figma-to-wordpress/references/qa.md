# QA: numbers first, per phase, the fix loop, until 0

QA after a phase **collects**: it adds findings to the list and fixes nothing, except a blocker. After phase 4 the
whole list is fixed, then QA runs over everything again until it finds 0. Numbers come first: the check script
measures, and pictures are opened only for what failed.

## 1. The check script (every section, every phase)

```
node <kit>/scripts/check.mjs --base <local url> --progress _figma/progress.json
node <kit>/scripts/check.mjs --base <local url> --route <path> --page <slug> --section <slug>   # one section
```

Per route, at the designed widths (default 1440 and 375, `--widths`):

- **Page:** HTTP status, console errors, horizontal overflow, text cut by its box ("clipped text"; line clamps and
  ellipses are allowed), one H1, images without `alt`, broken or soft images at DPR 2, lazy images above the fold,
  temporary Figma asset URLs, title, meta description, canonical, `lang`.
- **Section box:** every `data-section` box against the spec's `box@W` line.
- **Pixel diff:** each section against Figma's render of it, when `_figma/qa/figma/<page>--<section>@<W>.png`
  exists (section 3). The section is shot at CSS scale with motion off, lazy images loaded and fonts ready. A
  failure keeps `<page>--<section>@<W>-diff.png` and `-site.png` in `_figma/qa/diff/`.
- **Elements:** each `el@W` line in the spec (headings, text, buttons, images), measured from computed styles.
- **States:** each `state@W` line: the script hovers, focuses (keyboard style), clicks or swipes, waits
  `--settle` ms (default 400), then measures. One fresh page load per state.

At the sweep widths (default 320, 768, 1024, 1280, 1920, `--sweep`): overflow and clipped text only.

Full JSON in `_figma/qa/check-<time>.json`, full-page shots in `_figma/qa/shots/`; the screen shows one summary
line and at most 30 issue lines. Exit 0 = no issues, 1 = issues, 2 = the check could not run.

Needs, in the theme or the Next.js app: `npm i -D playwright pixelmatch pngjs` and `npx playwright install
chromium` (it falls back to the installed Chrome). In Git Bash a route like `/about/` is fine.

## 2. Spec lines the script reads

In `_figma/spec/<page>--<section>.md`, one per line (a leading `- ` is fine), values from Figma, never by eye:

```
box@1440: w=1440 h=760
el@1440: "Our services" font=Inter size=40 weight=600 line=48 tracking=-0.8 color=#15202b
el@1440: .services a.button bg=#f5412c color=#ffffff radius=8
el@375: img.hero-photo w=343 h=257 fit=cover pos="50% 30%"
state@1440: hover .services a.button bg=#c2321f
state@1440: focus "Book now" focusring=1
state@375: click .menu-toggle => .mobile-menu visible=1
state@375: swipe .testimonials .swiper => .swiper-slide:nth-child(2) visible=1
```

- **Target:** `"quoted text"` (the innermost element whose text starts with it) or a CSS selector, inside the
  section. `state@W: <hover|focus|click|swipe> <target> [=> <other target>] <props>` acts on the first target and
  measures the second (or the same one).
- **Props:** `font` (family name), `size`, `weight`, `line` (line height px), `tracking` (letter spacing px),
  `color`, `bg` (hex, `#rrggbbaa` for alpha), `w`, `h`, `radius`, `opacity`, `fit`, `pos` (object-fit and
  object-position: the crop), `visible` (1 or 0), `focusring` (1 or 0). Quote a value with spaces.
- **Which lines:** every heading level and body text style used in the section, every button (and its hover and
  focus), every image (box and crop), and each interactive state Figma has as a variant or a prototype frame (menu
  open, tab two, accordion open, next slide). Figma has no variant for a state: the gap's built look goes in the
  spec, marked "(gap)".

## 3. Figma renders for the pixel diff

For each section and designed width, once, when its spec is written: Figma's `get_screenshot` for that node with
`maxDimension` set to the node's longer edge (so the render is 1x). Download the returned URL straight to
`_figma/qa/figma/<page>--<section>@<W>.png` with the shell (curl); never ask for the image in the chat. No URL
option (an older server): `download_assets` with `defaultScale` 1, or skip the pixel diff for that section and say
so in the spec. Content that differs on purpose (a live date, a map, a carousel mid-slide) is a known diff:
note it in the spec and judge that section by its element lines.

## 4. Pass marks

Defaults until the first real build sets the final ones (those go into this table and the report names them):

| Check | Passes when | Option |
|---|---|---|
| Section box | within 1 px at 1440, 2 px at 375 | `--tol 1440:1,375:2` |
| Pixel diff | at most 2% of the section's pixels differ (pixelmatch threshold 0.1, anti-aliasing ignored) | `--max-diff 0.02` |
| Font size / line height / letter spacing | within 0.5 / 1 / 0.1 px | `--marks size=0.5,line=1,tracking=0.1` |
| Weight, family, object-fit, object-position, visible, focus ring | exact | |
| Colour and background | each channel within 3 of 255, alpha within 0.02 | `--marks color=3` |
| Element box, radius, opacity | the section box tolerance; 0.5 px; 0.02 | `--marks radius=0.5,opacity=0.02` |

The report lists the marks used. A mark changed for a project is a decision, with its reason.

## 5. Long content (phases 2 and full QA)

A test page shows the design still holds after the client edits. WordPress: a page `qa-long-content`, title
starting `[QA-LONG]`, with every layout and every field filled long (headings and buttons about three times the
Figma copy, one 30-character word, paragraphs four times, repeaters at twice the rows, an image of the wrong
ratio). Next.js: a route `/qa-long-content` built from a long copy of the content file. Run the check on it at the
designed and sweep widths; its findings are overflow, clipped text and broken layout (it has no Figma render). It
is removed before live (by its ID; the `[QA-LONG]` marker finds it).

## 6. The read-only check (every phase)

A fresh read-only check that changes nothing (in Claude Code: a subagent on a cheaper model such as Sonnet; in
other tools: a new chat told to only read). Its brief (fill the brackets):

> Read-only QA of [site] after phase [n]. Change nothing. Read `_figma/progress.json`, the phase checklist below
> and the check's latest JSON in `_figma/qa/`. Start from the numbers: every failing line there is a finding. Open
> images only for those failures (`_figma/qa/diff/`, the Figma render in `_figma/qa/figma/`), to say what differs.
> Then the checklist items the script can't measure. Return findings only, one line each: severity (blocker,
> major, minor), page/section, what is wrong, what Figma shows, what the site shows. No style opinions. At most 40
> lines.

It returns findings; the building chat adds them (`progress.py finding add`), merging duplicates.

## 7. Checklists (the read-only check uses the one for the phase)

- **Setup:** site loads, admin or dev server works, plugins or packages as planned, tokens and fonts render, no
  notices or console errors, private files answer 403 (WordPress) or are outside `public/` (Next.js).
- **Pages:** the check is clean at 1440 and 375 (boxes, pixels, elements, states); between widths nothing breaks;
  the long content page holds; menus and mobile menu work by mouse, touch and keyboard; sliders drag; video plays
  as designed; every page editable in ACF and the edit shows on the page (WordPress); no hard-coded content that
  belongs in a field; every section has its el and state lines.
- **Forms and email:** every form submits locally, validation and error states, thank-you redirect, the email
  arrives (local mail capture) with the right layout, recipients and reply-to; spam protection on.
- **SEO, security, speed:** one H1 and heading order, titles and descriptions, canonicals, Open Graph, sitemap,
  robots, schema valid, thank-you noindex, 404 real; no secrets in code; headers and hardening; LCP image preloaded,
  images sized, fonts swap, little JS; local Lighthouse as a regression guard only.
- **Full QA (the loop):** all of the above over every route.

## 8. Findings

- One list in `progress.json`: `progress.py <dir> finding add --severity <blocker|major|minor> --page <slug>
  --section <slug> --what "..." --expected "<Figma value>" --measured "<site value>"`.
- **Blocker:** the site breaks or the next phase can't start: fix at once, then `finding fix`.
- **Fix step:** work the list top down (blockers, major, minor), one finding at a time; re-run the check for that
  section and width; `progress.py <dir> finding fix <id> --how "<what changed, how verified>"`.
- **Decided:** only with numeric proof that Figma itself is inconsistent (two frames disagree), or a client item
  outside the build: `progress.py <dir> finding decide <id> --why "..."`. Listed in the report.
- **Full QA:** the script over every route and the read-only check with the full checklist. New findings: add, fix,
  run again. Stop when a full run finds 0. Then `progress.py <dir> set '*' '*' checked`.
