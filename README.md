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
- **1:1, by numbers**: every section within 1 px of Figma at 1440 and 2 px at 375, then a pixel diff against
  Figma's render and checks of each heading, text, button and image (font, size, weight, line height, letter
  spacing, colour, crop) and of hover, focus, menus, tabs and sliders. Images are opened only for failures.
  Nothing cut or overflowing at other widths, also with every field filled long; images sharp on retina screens.
- **Optimized by default**: SEO standard, speed built in (PageSpeed Insights aimed at a pass, not a must; the design
  is never changed for a score).
- **A progress page** shows what is happening now and what is done: Now/Next and the update time at the top,
  phases, every page's sections with their status, every QA finding with its status, a short log. In Claude it is
  live (the page reads its own database, so it updates itself); in other tools a static page is republished at every
  unit end and every stop.

## Requirements

- An AI coding tool that reads Agent Skills and runs commands (Claude Code, Codex, Antigravity, Cursor, OpenCode,
  Cline, Devin Desktop...) with a **Figma MCP server** connected (Figma's remote server or the desktop app's).
- Python 3 and Node.js 18+; for the check script `npm i -D playwright pixelmatch pngjs` and `npx playwright install
  chromium`.
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

Other AI tools: link the same clone's `skills/figma-to-wordpress/` into the tool's skills folder under the name
`figma-to-wordpress` (for example `~/.agents/skills/` for Codex, Cursor and Devin Desktop, `~/.gemini/config/skills/`
for Antigravity, `~/.config/opencode/skills/` for OpenCode). The steps are plain words; where a step names a Claude
tool, SKILL.md > In other tools gives the fallback (the question tool, subagents, the progress page as a local file
that reloads itself, the context meter, connecting the Figma MCP server), with convert-to-wordpress's
`references/agents.md` > Per tool. Every script is Python or Node, so it runs in PowerShell too.

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
skills/figma-to-wordpress/references/ figma, wordpress, nextjs, qa, progress, start, phase-steps, live
skills/figma-to-wordpress/scripts/    progress.py and live.py (progress page), check.mjs (browser check),
                                      oneoff.py (the self-check searches)
tests/                                tests for the scripts
CHANGELOG.md                          what changed in each version
AGENTS.md                             rules for changing the skill
```

## Licence

MIT. See [LICENSE](LICENSE). Figma is a trademark of Figma, Inc.; WordPress is a trademark of the WordPress
Foundation; this project is not affiliated with either.
