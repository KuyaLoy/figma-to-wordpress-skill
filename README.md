# figma-to-wordpress

A Claude Code skill (packaged as a plugin) that builds a Figma design 1:1 as a website:

- **WordPress** by default: every page editable in ACF PRO, every form and email in Contact Form 7, Yoast SEO, a
  Tailwind theme on the design's tokens. Setup, fields, forms, SEO and launch come from the
  [convert-to-wordpress](https://github.com/KuyaLoy/convert-wordpress-skill) skill's kit.
- **Next.js** when the task asks for it: App Router, TypeScript, Tailwind tokens from Figma, `next/image`,
  `next/font`, the Metadata API.

How it works:

- **One chat builds the whole site.** No team of builder, tester and QA chats: those cost far more usage than the
  work needs.
- **The task first.** A Zoho (or other tracker) task's instructions win over the skill's defaults.
- **Inventory once**: pages, desktop and mobile frames, breakpoints, tokens, fonts, video, motion, hidden layers,
  design gaps. Then a short plan and your OK.
- **Phase by phase**: setup, pages (section by section, one small Figma call per section, values saved to disk),
  forms and email, SEO, security and speed. QA after each phase only collects findings; after the last phase the
  whole list is fixed, then QA runs again until it finds 0. Then your go, then live.
- **1:1**: every section within 1 px of Figma at 1440 and 2 px at 375, measured by the check script; nothing cut or
  overflowing at other widths; images sharp on retina screens.
- **Optimized by default**: SEO standard, speed built in (PageSpeed Insights aimed at a pass, not a must; the design
  is never changed for a score).
- **A progress page** shows what is done and what is not: phases, every page's sections with their status, open QA
  findings, a short log.

## Requirements

- Claude Code (the desktop app's Code tab or the CLI) with a **Figma MCP server** connected (Figma's remote server
  or the desktop app's).
- Python 3 and Node.js 18+; Playwright for the check script (`npm i -D playwright`, `npx playwright install
  chromium`).
- WordPress builds: a local web stack (Laragon, XAMPP, MAMP, Local...) and the convert-to-wordpress skill.

## Install

In a Claude Code chat:

```
/plugin marketplace add KuyaLoy/figma-to-wordpress-skill
/plugin install figma-to-wordpress@figma-to-wordpress
```

Then turn on automatic updates (once): `/plugin` > Marketplaces > figma-to-wordpress > Enable auto-update.

Or as a git clone (updates with `git pull --ff-only`): clone this repository and link
`skills/figma-to-wordpress/` into `~/.claude/skills/figma-to-wordpress`.

## Use

Open the project folder and say, for example: "Build this Figma design in WordPress: <Figma link>" (or paste the
task link). The skill reads the task, asks its intake questions once, inventories the design, shows the plan and
the progress page, and builds after your OK.

## Safety

The skill never writes a password, licence key or API key into the build or its notes. The default local admin
login is read from your local profile and only used on local sites; live passwords and keys are typed by you.
Nothing goes live before your go. Its planning files (`_figma/`) are never served and never committed.

## Layout

```
.claude-plugin/plugin.json            the plugin
.claude-plugin/marketplace.json       this repo as a one-plugin marketplace
skills/figma-to-wordpress/SKILL.md    the workflow and its rules
skills/figma-to-wordpress/references/ figma, wordpress, nextjs, qa, progress
skills/figma-to-wordpress/scripts/    progress.py (progress page), check.mjs (browser check)
tests/                                tests for the scripts
CHANGELOG.md                          what changed in each version
AGENTS.md                             rules for changing the skill
```

## Licence

MIT. See [LICENSE](LICENSE). Figma is a trademark of Figma, Inc.; WordPress is a trademark of the WordPress
Foundation; this project is not affiliated with either.
