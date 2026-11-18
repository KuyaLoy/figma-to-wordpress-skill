# Changelog

Every change to the skill, newest first. Versions follow [Semantic Versioning](https://semver.org); the format
follows [Keep a Changelog](https://keepachangelog.com).

## [Unreleased]

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
