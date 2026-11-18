# QA: per phase, the fix loop, until 0

QA after a phase **collects**: it adds findings to the list and fixes nothing, except a blocker. After phase 4 the
whole list is fixed, then QA runs over everything again until it finds 0.

## 1. The check script (every phase)

```
node <kit>/scripts/check.mjs --base <local url> --progress _figma/progress.json
```

- Designed widths (default 1440 and 375, change with `--widths`): HTTP status, console errors, horizontal overflow,
  one H1, images without `alt`, broken or soft images at DPR 2, lazy images above the fold, temporary Figma asset
  URLs, title, meta description, canonical, `lang`, and every `data-section` box against its spec
  (`box@1440: w=1440 h=760` lines in `_figma/spec/<page>--<section>.md`) within 1 px at 1440 and 2 px at 375.
- Sweep widths (default 320, 768, 1024, 1280, 1920): overflow only (nothing may be cut or scroll sideways).
- Full JSON and full-page screenshots in `_figma/qa/`; the screen shows a short summary. Exit 0 = no issues.
- Needs Playwright where it runs: `npm i -D playwright` (the theme or the Next.js app has a package.json) and
  `npx playwright install chromium`; it falls back to the installed Chrome. In Git Bash a route like `/about/` is
  fine (the script undoes Git Bash's path rewrite).
- One section while building: `--route <path> --page <slug> --section <slug>`.

## 2. The read-only check (every phase)

One subagent on a cheaper model (Sonnet), read-only, with this brief (fill the brackets):

> Read-only QA of [site] after phase [n]. Change nothing. Read `_figma/progress.json`, the phase checklist below,
> and the check's latest JSON in `_figma/qa/`. Compare the Figma screenshots in `_figma/qa/figma/` with the local
> screenshots in `_figma/qa/shots/` for [routes]. Return findings only, one line each: severity (blocker, major,
> minor), page/section, what is wrong, what Figma shows, what the site shows. No style opinions: only differences
> from Figma, broken behaviour, and the checklist. At most 40 lines.

It returns findings; the building chat adds them (`progress.py finding add`), merging duplicates.

## Checklists (the read-only check uses the one for the phase)

- **Setup:** site loads, admin or dev server works, plugins or packages as planned, tokens and fonts render, no
  notices or console errors, private files answer 403 (WordPress) or are outside `public/` (Next.js).
- **Pages:** each section matches Figma at 1440 and 375 (layout, spacing, type, colours, images, icons, order,
  copy verbatim); between widths nothing breaks; menus and mobile menu work by mouse, touch and keyboard; hover and
  focus states; sliders drag; video plays as designed; every page editable in ACF and the edit shows on the page
  (WordPress); no hard-coded content that belongs in a field.
- **Forms and email:** every form submits locally, validation and error states, thank-you redirect, the email
  arrives (local mail capture) with the right layout, recipients and reply-to; spam protection on.
- **SEO, security, speed:** one H1 and heading order, titles and descriptions, canonicals, Open Graph, sitemap,
  robots, schema valid, thank-you noindex, 404 real; no secrets in code; headers and hardening; LCP image preloaded,
  images sized, fonts swap, little JS; local Lighthouse as a regression guard only.
- **Full QA (the loop):** all of the above over every route.

## Findings

- One list in `progress.json`: `progress.py <dir> finding add --severity <blocker|major|minor> --page <slug>
  --section <slug> --what "..." --expected "<Figma value>" --measured "<site value>"`.
- **Blocker:** the site breaks or the next phase can't start: fix at once, then `finding fix`.
- **Fix step:** work the list top down (blockers, major, minor), one finding at a time; re-run the check for that
  route and width; `progress.py <dir> finding fix <id> --how "<what changed, how verified>"`.
- **Decided:** only with numeric proof that Figma itself is inconsistent (two frames disagree), or a client item
  outside the build: `progress.py <dir> finding decide <id> --why "..."`. Listed in the report.
- **Full QA:** run the script over every route and the read-only check with the full checklist. New findings: add,
  fix, run again. Stop when a full run finds 0. Then `progress.py <dir> set '*' '*' checked`.
