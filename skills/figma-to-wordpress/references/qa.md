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

`_figma/qa/design-check.json` (the latest run) holds every measured value in the row shape convert-to-wordpress's
`design-check` writes too, so one reader handles both: `{"tool": "figma-check", "version": 1, "rows": [{"check":
"box|pixel|el|state|page", "route", "width", "selector", "state", "prop", "ref", "got", "pass", "image"}],
"summary": {"pass": n, "fail": n}}`. `ref` is Figma's value, `image` a diff image for failing pixel rows only.

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

A test page shows the design still holds after the client edits: every layout and every field filled long
(headings and buttons about three times the Figma copy, one 30-character word, paragraphs four times, repeaters
at twice the rows, an image of the wrong ratio).

- **WordPress, convert-to-wordpress kit 0.9 or later:** its `long-content.php` (the kit's `scripts/parity/`, the
  built theme's `tests/parity/`). `php long-content.php make <route>` once per page makes a noindex copy at
  `/kit-long-test-<page>/` (the front page: `kit-long-test-home`), marked by the post meta `_<prefix>_long_test`;
  `list` prints their IDs and paths; `remove` deletes exactly those IDs, before live. Its `references/build.md` >
  "Design checks: states, motion, long content" has the details.
- **WordPress, older kit:** one page by hand, `qa-long-content`, title starting `[QA-LONG]`; removed before live
  by its ID (the marker finds it).
- **Next.js:** a route `/qa-long-content` built from a long copy of the content file; deleted before live.

Run `check.mjs` on the test pages at the designed and sweep widths; its findings are overflow, clipped text and
broken layout (they have no Figma render).

## 6. The read-only check (every phase)

A fresh read-only check that changes nothing (in Claude Code: a subagent on a cheaper model such as Sonnet; in
other tools: a new chat told to only read). Its brief (fill the brackets):

> Read-only QA of [site] after phase [n]. Change nothing. Read `_figma/progress.json`, the phase checklist below
> and the check's latest JSON in `_figma/qa/`. Start from the numbers: every failing line there is a finding. Open
> images only for those failures (`_figma/qa/diff/`, the Figma render in `_figma/qa/figma/`), to say what differs.
> Then the checklist items the script can't measure. Then review the code the phase changed (`git diff` since the
> last phase gate) against the code checklist and the self-check output. Return findings only, one line each:
> severity (blocker, major, minor), page/section or file:line, what is wrong, what Figma or the rule says, what
> the site or code does. No style opinions beyond the rules. At most 40 lines.

It returns findings; the building chat adds them (`progress.py finding add`), merging duplicates. The code review
runs at every phase gate, not only the first ones.

## 7. Code gates and the self-check (every phase gate, and before DONE)

SKILL.md rule 13 in commands. Run in the theme (WordPress) or the app (Next.js); every failure is a finding.

- **PHPCS** (WordPress): `vendor/bin/phpcs` with the theme's `phpcs.xml`, where the theme's own escaping and
  sanitising helpers are registered (`WordPress.Security.EscapeOutput` property `customEscapingFunctions`, and
  `customSanitizingFunctions` where used). No `phpcs:disable` and no blanket `phpcs:ignore`; one narrow ignore only
  with a reason on the same line.
- **Prettier and ESLint:** `npx prettier --check .` and `npx eslint .` (Next.js: `npm run lint`), with the
  project's configs; build output, vendor and node_modules ignored.
- **Self-check** (grep, or rg the same patterns), over the theme's or app's source; each hit is fixed or kept with a
  one-line reason in the report:

```
X="--exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=dist --exclude-dir=build --exclude-dir=.next"
grep -rnE $X --include='*.php' --include='*.js' --include='*.jsx' --include='*.tsx' -e '[a-z]-\[(#|[0-9])' .
grep -rnE $X --include='*.css' -e '#[0-9a-fA-F]{3,8}\b' . | grep -v tokens
grep -rnE $X --include='*.php' --include='*.js' --include='*.tsx' -e '[0-9]+:[0-9]+|\b[A-Z][A-Z0-9]+-T[0-9]+\b' .
grep -rn $X --include='*.php' -e 'phpcs:ignore' -e 'phpcs:disable' .
```

  In order: one-off values, hex outside the tokens file, Figma node IDs and ticket tags, ignore comments. The
  node-ID pattern also matches times and ratios: read the hits, fix only node IDs.
- **Size and shape:** no section template or component over about 250 lines or 15 fields or props (split it); one
  job per file (form logic, markup and JS apart); no inline `<script>` (WordPress: enqueued; Next.js: imported);
  no kit file, helper, config or seed file the site doesn't use.

## 8. Checklists (the read-only check uses the one for the phase)

- **Setup:** site loads, admin or dev server works, plugins or packages as planned, tokens and fonts render, no
  notices or console errors, private files answer 403 (WordPress) or are outside `public/` (Next.js); the starter
  chosen by the rule and the reason in the plan; only the kit files the site uses.
- **Pages:** the check is clean at 1440 and 375 (boxes, pixels, elements, states); between widths nothing breaks;
  the long content test pages hold; menus and mobile menu work by mouse, touch and keyboard; sliders drag; video
  plays as designed; every page editable in ACF and the edit shows on the page (WordPress); no hard-coded content
  that belongs in a field; every section has its el and state lines.
- **Code (every phase):** section 7 is clean; values come from tokens; a shared map (colours, variants) exists once;
  sections reuse parts instead of copying them; comments say why, with no Figma node IDs or ticket tags.
- **Forms and email:** every form submits locally, validation and error states, thank-you redirect, the email
  arrives (local mail capture) with the right layout, recipients and reply-to; spam protection on.
- **SEO, security, speed:** one H1 and heading order, titles and descriptions, canonicals, Open Graph, sitemap,
  robots, schema valid, thank-you noindex, 404 real; no secrets in code; headers and hardening; LCP image preloaded,
  images sized, fonts swap, little JS; local Lighthouse as a regression guard only.
- **Full QA (the loop):** all of the above over every route.

## 9. Findings

- One list in `progress.json`: `progress.py <dir> finding add --severity <blocker|major|minor> --page <slug>
  --section <slug> --what "..." --expected "<Figma value>" --measured "<site value>"`.
- **Blocker:** the site breaks or the next phase can't start: fix at once, then `finding fix`.
- **Fix step:** work the list top down (blockers, major, minor), one finding at a time; re-run the check for that
  section and width; `progress.py <dir> finding fix <id> --how "<what changed, how verified>"`.
- **Decided:** only with numeric proof that Figma itself is inconsistent (two frames disagree), or a client item
  outside the build: `progress.py <dir> finding decide <id> --why "..."`. Listed in the report.
- **Full QA:** the script over every route and the read-only check with the full checklist. New findings: add, fix,
  run again. Stop when a full run finds 0. Then `progress.py <dir> set '*' '*' checked`.
