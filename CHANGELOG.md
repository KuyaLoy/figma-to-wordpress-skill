# Changelog

Every change to the skill, newest first. Versions follow [Semantic Versioning](https://semver.org); the format
follows [Keep a Changelog](https://keepachangelog.com).

## [Unreleased]

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
