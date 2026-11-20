# Changelog

Every change to the skill, newest first. Versions follow [Semantic Versioning](https://semver.org); the format
follows [Keep a Changelog](https://keepachangelog.com).

## [Unreleased]

## [0.2.6] - 2026-11-20

### Changed

- The progress page shows what is happening and stays current, the same page and keys as convert-to-wordpress
  0.9.5: at the top, in large type, Now (the step and the time it started), Next, anything waiting or blocked, and
  the time the page was rendered ("n min ago" from one tiny inline script). New command
  `progress.py <dir> now "<step>" [--next ...] [--waiting ...] [--blocked ...]`.
- Every QA finding is listed with its status (open, fixed, decided), with counts per status and per QA run (the
  finding's `phase`; in the QA-until-0 loop `--phase "qa run <n>"`), open first, fixed and decided folded with
  how each was fixed or why it was kept.
- Publishing: at every unit end (the plan, each page built, each QA run collected, each fix batch, QA at 0, live)
  and every stop, and before a long step (write `now`, publish, then start); the same link as before. Replaces
  "only at the plan, once per finished page and at each phase end".
- progress.json: additions only, `now` (`step`, `started`), `next`, `waiting`, `blocked`; `updated` is the time of
  the last write or render. A file made before 0.2.6 still loads and renders. `render` now saves the update time.

## [0.2.5] - 2026-11-20

### Added

- The leads portal, mandatory on a live site with a lead form (a site without one says so in the plan): each lead
  is also posted to the portal whether the email went out or failed; the code is in from phase 3, the endpoint and
  key go in on live only, a GET check (stores nothing) proves them before the switch, then one TEST lead per form.
  The portal's address comes from the developer's profile or the task, never from the skill.
- WordPress: `references/wordpress.md` points to convert-to-wordpress 0.9.4's rule (its `references/forms-email.md`
  > The leads portal) in phase 3, and the live checklist summary names its leads portal item and `leads-check.py`.
- Next.js: `references/nextjs.md` phase 3 adds a server-only `sendLead()` (`form`, `idempotency_key`, the fields,
  `source_url`, `ip_address`, `gclid`, `fbp`, `fbc`; Bearer key; 5 second timeout; 200 and 202 delivered; a failure
  logged with the status only, never blocking the visitor), off unless `LEADS_ENDPOINT` and `LEADS_WRITE_KEY` are
  set, which they are only for Production on the host. Live: the GET check, then one TEST lead per form.
- SKILL.md: the phase 3 row, a Leads portal item under Live, Live QA (each test lead reaches the email and the
  portal) and "Done means".

## [0.2.4] - 2026-11-20

### Changed

- The cache plugin, as convert-to-wordpress: every live WordPress site gets the live checklist's cache plugin
  (LiteSpeed Cache unless the profile's `cache_plugin` names another), never locally or on staging. A heavy design
  only uses more of its options on live (page and browser cache first, then CSS and JS one at a time, each with a
  parity check), never a second speed plugin. SKILL.md rule 6 and `references/wordpress.md` > Phase 4, pointing to
  the kit's `references/seo-security.md` > Performance.

## [0.2.3] - 2026-11-20

### Changed

- Live: the WordPress rules are the same as convert-to-wordpress's, so the skill points to its live plugin checklist,
  the one list (its `assets/launch/RUNBOOK.template.md` section 4 and `references/launch.md` > After the installer),
  instead of naming "a WebP conversion plugin and Contact Form CFDB7": the profile's live plugins from the
  developer's plugin folder (versions checked before go-live), Contact Form CFDB7, Converter for Media, the
  reCAPTCHA v3 keys and the cache plugin (LiteSpeed Cache by default). Staging gets none of it. SKILL.md's Live row,
  Live section and "Done means", and `references/wordpress.md` > Live.
- `references/wordpress.md` step 4: ACF PRO is activated by the profile's `acf_pro_license`, written only into local
  wp-config files by the kit's `make-wp-config.py`, not pasted by the developer.

## [0.2.2] - 2026-11-19

Starter rule and code quality, from a read-only audit of a large Figma build (no bugs, but about 2,000 one-off
values, a copied colour map, an oversized section, node IDs and ticket tags in comments, unused kit files, PHPCS
passing through ignore comments, code review only in early phases).

### Changed

- `references/wordpress.md`: the starter by rule, not "_tw by default". Clearly easier in Tailwind (a design system
  with repeating tokens, many reusable sections): _tw. A normal site that doesn't really need Tailwind: Barebones
  with CSS-variable tokens. A Figma design is never a Tailwind source. The plan states the choice and one reason.
- QA: the read-only check also reviews the code each phase changed, at every phase gate.

### Added

- SKILL.md rule 13, clean code: tokens not one-offs, ship only what is used, comments say why (no Figma node IDs or
  ticket tags), size limits (about 15 options or 250 lines; one job per file; no inline JS), gates (PHPCS with the
  theme's escaping helpers registered, Prettier, ESLint, the self-check) at every phase gate and before DONE.
- `references/qa.md` section 7: the code gates and four self-check greps (one-off values, hex outside the tokens
  file, node IDs and ticket tags, ignore comments); a code checklist for every phase.
- `references/nextjs.md`: no arbitrary values, Prettier with the Tailwind plugin, unused starter files removed.

## [0.2.1] - 2026-11-18

### Fixed

- Long content on WordPress: `references/qa.md` now names convert-to-wordpress 0.9's `long-content.php` (the
  kit's `scripts/parity/`, the theme's `tests/parity/`; `make <route>` per page, `list`, `remove`: noindex copies at
  `/kit-long-test-<page>/`, removed by their stored IDs), not `design-check.mjs --long`, which only checks them.
  `qa-long-content` with `[QA-LONG]` stays for an older kit; Next.js keeps its `/qa-long-content` route. SKILL.md's
  live check says "the long content test pages removed".

## [0.2.0] - 2026-11-18

Closer to the design, checked by numbers; fewer publishes; usable from other AI tools.

### Added

- `scripts/check.mjs`: a pixel diff of each section against Figma's 1x render
  (`_figma/qa/figma/<page>--<section>@<W>.png`, pixelmatch and pngjs loaded from the project), the section shot at
  CSS scale with motion off and images loaded; a failing diff keeps its diff and site images in `_figma/qa/diff/`.
- `el@W` spec lines: font family, size, weight, line height, letter spacing, colour, background, box, radius,
  opacity, object-fit and object-position of headings, text, buttons and images, targeted by quoted text or a
  selector inside the section.
- `state@W` spec lines: hover, focus, click or swipe a target, then measure it (or another target: an open menu, a
  tab, the next slide) against Figma's variant, including `visible` and `focusring`.
- "Clipped text" on every run: text cut by an overflow-hidden box (line clamps and ellipses allowed).
- Pass marks as defaults until the first real build sets them (`references/qa.md`): box 1 px at 1440 and 2 px at
  375, pixel diff 2%, size 0.5 px, line height 1 px, letter spacing 0.1 px, colour 3/255; options `--max-diff`,
  `--marks`, `--settle`, `--no-pixel`, `--no-states`.
- Long content: a `qa-long-content` test page (`[QA-LONG]` marker) with every field filled long, checked in phase 2
  and full QA, removed before live.
- `_figma/qa/design-check.json`: every measured value as a row (`check`, `route`, `width`, `selector`, `state`,
  `prop`, `ref`, `got`, `pass`, `image`) with a pass and fail summary, the same shape convert-to-wordpress 0.9's
  `design-check` writes, so one QA reader handles both. On WordPress the long content page comes from that kit.
- `tests/check.test.mjs` (spec parsing and comparisons), run by the `check` workflow.

### Changed

- The progress page is published at the plan, once per finished page and at each phase end; `progress.json` still
  updates per section.
- The read-only QA check reads the numbers first and opens images only for failures.
- Tool-neutral steps: the read-only check is a Sonnet subagent in Claude Code and a new read-only chat elsewhere; a
  stop report goes to Command Center as a message in the Claude desktop app and as a line under `## Stops` in
  notes.md elsewhere. README lists other AI tools and their skills folders.
- Figma renders are downloaded by `get_screenshot`'s URL straight to disk, never brought into the chat.

## [0.1.1] - 2026-11-18

### Changed

- `references/wordpress.md` names convert-to-wordpress's `references/wordpress-essentials.md` (its 0.8.0) and its
  one-go setup scripts (`get-wordpress.py`, `make-wp-config.py`, `install-wp.py` with the profile's `local_admin`),
  instead of only pointing at its SKILL.md.

## [0.1.0] - 2026-11-18

First version: a Figma design built 1:1 as a WordPress or Next.js site by one chat, phase by phase.

### Added

- `SKILL.md`: one chat builds the whole site (no builder, tester or QA chats); the task's instructions first;
  intake once; the design inventoried once; a short plan and the plan gate; phases 1 Setup, 2 Pages (section by
  section, one Figma node per call, values saved once to `_figma/spec/`), 3 Forms and email, 4 SEO, security and
  speed; QA after each phase only collects findings (a blocker is fixed at once); then the whole list is fixed and
  full QA runs until it finds 0; the go-live gate; live; the report.
- Done standard: every section within 1 px of Figma at 1440 and 2 px at 375; nothing cut or overflowing between
  and beyond the designed widths; images sharp at DPR 2.
- Best practice by default: semantic and accessible markup, SEO standard, speed built in; PageSpeed Insights aimed
  at a pass, not a must; a speed plugin for heavy WordPress designs; the design never changed for a score.
- WordPress through the convert-to-wordpress kit (read by path, not copied): local setup in one go with the
  developer's default local admin from their local profile, ACF PRO from their zip, Contact Form 7, Yoast, the
  Tailwind starter theme; the WebP conversion plugin and Contact Form CFDB7 on live at launch.
- Next.js: App Router, TypeScript, Tailwind tokens from Figma, `next/font`, `next/image`, the Metadata API, server
  actions for forms, security headers.
- `scripts/progress.py`: pages x sections x status, phases, findings and a log in `progress.json`; renders a
  self-contained progress page to publish as a private artifact.
- `scripts/check.mjs`: Playwright check at 1440 and 375 plus an overflow sweep; section boxes against the Figma
  spec; summary on screen, full result and screenshots on disk.
- References: `figma.md`, `wordpress.md`, `nextjs.md`, `qa.md`, `progress.md`.
- Release automation as the other skill repos: `check` (validate, tests, release guard) and `release` (tag
  `figma-to-wordpress--v<version>` and the GitHub Release).
