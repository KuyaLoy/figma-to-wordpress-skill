---
name: figma-to-wordpress
description: Builds a Figma design 1:1 as a WordPress site (every page editable in ACF PRO, forms in Contact Form 7, Yoast SEO) or as a Next.js site (App Router, TypeScript, Tailwind), in one chat. The task's instructions come first, the design is inventoried once, then the build runs phase by phase (setup, pages section by section, forms and email, SEO, security and speed) with QA that only collects findings, one fix loop until QA finds 0, the developer's go, then live. A progress page shows what is done and what is not. Use whenever a Figma file or link has to become a website, for requests like "build this Figma design", "Figma to WordPress", "Figma to Next.js", "turn this Figma into a website", "code this design from Figma" or "make this Figma page in WordPress".
license: MIT
---

# Figma to WordPress (or Next.js), 1:1

A Figma design becomes a real website that matches it at the designed widths, works at every width in between,
and is fast, findable and safe. WordPress by default: every page editable in ACF PRO, every form in Contact Form 7.
Next.js when the task asks for it. One chat does the whole build; the developer sees progress on one page.

**The yardstick:** 1:1 with Figma, built the way a senior developer would, straight to the point, low on usage.

## The kit

Paths are relative to this file's folder. Read a reference only when its step comes up.

| Path | What | Read when |
|---|---|---|
| `references/figma.md` | Figma MCP calls, the inventory, tokens, assets, design gaps | Start, and every section |
| `references/wordpress.md` | The WordPress target: what comes from convert-to-wordpress, what differs | Target WordPress |
| `references/nextjs.md` | The Next.js target: stack, tokens, images, fonts, metadata, deploy | Target Next.js |
| `references/qa.md` | The check script, spec lines, pass marks, long content, the read-only check, the fix loop | First section; end of each phase |
| `references/progress.md` | progress.json and the progress page | Start; when publishing |
| `references/live.md` | The launch per target, the leads portal, live QA, the report | Go-live gate; the report |
| `scripts/progress.py` | Now/Next, pages, sections, statuses, findings, log; renders the progress page | Every step |
| `scripts/live.py` | The live progress page and its database rows (called by progress.py) | Never by hand |
| `scripts/oneoff.py` | The self-check searches in Python, for any shell | Every phase gate |
| `scripts/check.mjs` | Numbers at 1440 and 375 (boxes, pixel diff against Figma, type, colour, images, states) plus an overflow sweep; summary only | Every section, every phase |

WordPress builds also use the **convert-to-wordpress** skill's kit (setup scripts, theme, fields, forms, SEO,
launch): `references/wordpress.md` says which parts and where to find it. Never copy its rules here; read them there.

## In other tools (Codex, Antigravity, T3 Code and others)

The steps are plain words. Where one names a Claude tool, open convert-to-wordpress's `references/agents.md` > Per
tool (0.9.14 or later: install folders, loading the skill, asking, subagents, the browser, the context meter, the
title) and do what its column says. This skill's own steps there:
- **Figma:** the Figma MCP server connected in this tool (`references/figma.md` > In other tools), else a blocker.
- **Asking:** the tool's question tool; without one, numbered options with the recommended one first, then wait.
- **The read-only QA check:** a subagent (Codex `spawn_agent`, Antigravity `invoke_subagent`), not a new chat.
- **Browser steps** (wp-admin, live checks, test leads): Antigravity drives the lead's Chrome through the
  chrome-devtools MCP (the kit's Per tool line and tab rules, 0.9.16 or later); its own pane only as a fallback.
- **The progress page:** the local file, `progress.py <dir> render --refresh 30 --open` once (`references/progress.md`).
- **Context:** Codex `/status`; no meter (Antigravity): checkpoint at every page end and phase end.
- **Shell:** every script is Python or Node; on Windows `py -3` or `python` where a step says `python3`.

## Rules (always)

1. **One chat builds the whole site.** No builder, tester or QA chats, no helpers for building. The only other
   agent is the read-only QA check at the end of each phase. (Learned 18 Nov 2026: a six-chat build spent 79% of
   its usage on chats re-reading their own history.)
2. **The task first.** A Zoho (or other tracker) task's instructions win over this skill's defaults. Read all of
   it (description, linked docs, comments, attachments) before the inventory and save it verbatim to
   `_figma/brief.md`. Follow it verbatim: copy, icons, emoji, long titles, no rewording.
3. **1:1 from real values, checked by numbers.** Build from Figma's data (`get_design_context`, variables), never
   by eye from a screenshot. Done standard at the designed widths (usually 1440 and 375): every section's box
   within 1 px of Figma on desktop and 2 px on mobile, and inside it the pixel diff, type, colours, images and
   states within the pass marks (`references/qa.md`). Between and beyond them nothing overflows, is cut, squashed
   or stretched, also with long content. A mismatch is accepted only with numeric proof that Figma itself is
   inconsistent; log it as a decision.
4. **Small Figma calls.** One node per call: the section being built, desktop and mobile. Save what it returns once
   to `_figma/spec/` and re-read the file, never the page again. Large pages: `get_metadata` first, then one section.
5. **Straightforward.** Decide what has a sensible default and log it (`progress.py log`, and "Decisions" in the
   report). Ask the developer only about blockers. Design gaps (open menu, hover and focus states, form states,
   thank-you, 404, empty states) are built from the design system, never a new look, and listed.
6. **Best practice by default.** Semantic HTML, one H1, headings in order, alt text, labels, keyboard and visible
   focus, no console errors or PHP notices, escaped output, sanitised input. SEO standard (titles, descriptions,
   canonicals, Open Graph, sitemap, schema where it fits). Speed built in from the first section: sized responsive
   images, the LCP image preloaded and never lazy, the rest lazy, self-hosted fonts with `swap`, little JavaScript,
   loaded only where used. PageSpeed Insights aims at a pass but is not a must; the design is never changed for a
   score. Every live WordPress site gets the live checklist's cache plugin (LiteSpeed Cache unless the profile
   names another); a heavy design only uses more of its options, never a second speed plugin
   (`references/wordpress.md`).
7. **Assets exactly as in Figma.** Every image and SVG exported from Figma into the project, in its exact slot, at
   2x for raster images (sharp at DPR 2), people never cut by a crop. No temporary Figma asset URLs left in code.
   Edits a Figma export can't give (background removal, extending an image) only with a tool the developer has,
   true to the source, and listed in the report.
8. **Secrets stay out.** No password, licence key or API key in the repo, the theme, `_figma/`, the progress page or
   any report. The local default admin login comes from the developer's local profile at run time and is for local
   sites only; live passwords, licence keys and API keys are typed by the developer.
9. **Live only after the developer's go.** A backup before any live change, one change at a time, a rollback named.
10. **Spend less.** Scripts write big output to disk and print a summary. Read summaries, not whole files. Never read
    node_modules, vendor, minified, lock or build files. Numbers first: open an image only for a failing check,
    cropped to the problem. Figma renders go to disk by URL, never into the chat.
11. **Never stop silently.** Every turn that ends without the work going on (plan ready, a phase's QA done, a
    checkpoint, a block, waiting for a go) ends with a short stop report: what was done, the state, decisions taken,
    and last `Next: <step> — waiting on <who>`. The progress page says the same (`progress.py now`, publish). In a
    Command Center project it also goes to Command Center (in the Claude desktop app: a message to the parent chat;
    in other tools: a line under `## Stops` in notes.md). **Running, not stopped:** a turn that ends while its own
    work keeps running (a background command, a subagent, a check) starts its last message, its recap and the
    progress page's Now line with `RUNNING, not stopped: <what>, started HH:MM; I continue by myself when it
    finishes.` (the time from the clock); a real stop never says RUNNING, it says what it waits on. **The title
    too** (Claude desktop app: `set_session_title` with "self"; other tools: > In other tools): `▶ RUNNING | `,
    `⏸ WAITING on <who> | `, `✋ BLOCKED | `, `✓ DONE | ` (also in review) at the front of the chat's own title,
    one call per state change, the rest unchanged, never for anything else (`references/progress.md` > Publishing).
12. **Context watch.** Check your context % (the tool's own meter: > In other tools) before each section. From 50%:
    finish the section, write `_figma/checkpoint.md` (task, go quoted, done so far, state, exact next step), report
    CHECKPOINT and end the turn. At 75%: the same at the first safe point. Where the thresholds allow, checkpoint at a
    page or phase end rather than inside a section or a QA run. The checkpoint names the exact next step (the command,
    the page and section, the route), not "continue QA". `progress.json` and the checkpoint are enough to resume cold.
13. **Clean code: reusable, simple, no spaghetti.** (Learned 19 Nov 2026: a large Figma build had no bugs, but about
    2,000 one-off values, a colour map copied about nine times, a 399-line section, Figma node IDs and ticket tags in
    hundreds of comments, unused kit files shipped, and PHPCS passing only through ignore comments.)
    - **Tokens, not one-offs:** a design value with no token gets one (`@theme` or a CSS variable), never
      `text-[19px]`, `bg-[#...]` or a hex in CSS; a shared map (colours, variants) lives once.
    - **Ship only what is used:** only the kit files the build uses; no unused helpers, empty configs or seed files
      in the theme or app.
    - **Kit files as shipped; checks with their output** (WordPress: the kit's rule 16, 0.9.12 or later): a kit file
      is copied with the prefix swap only; any site change to one is listed with its reason (the file, the change,
      why) in the task's notes. A check is reported only with its output (the tool's OK or FAIL line and counts,
      pasted), never "passes", "seeded" or "0 private" from memory.
    - **Comments say why:** no Figma node IDs, no ticket tags; history lives in git.
    - **Size limits:** split a section past about 15 options or 250 lines; one job per file (logic, markup and JS
      apart); JS enqueued or imported, never inline.
    - **Gates:** PHPCS passes with the theme's escaping helpers registered (no blanket ignore comments), Prettier
      and ESLint pass, and the self-check finds nothing (`references/qa.md`), at every phase gate and before DONE.

In a Command Center project (handoff.md says `Mode: Command Center`) this chat is a task chat: its Worker rules
apply as well (go quoted in notes.md, stop messages, no Zoho posts). Where they and this skill differ, they win.

## Start

1. **Resuming?** If `_figma/` exists: read `_figma/checkpoint.md` (if any) and run `python3 <kit>/scripts/progress.py
   <project>/_figma status`. Re-check only what can have changed since: the site or dev server answers (and the
   database, on WordPress), and the files the checkpoint lists as touched (git status or their times). Don't
   re-read the whole plan or re-run QA; continue from its next step.
2. **The task.** Read it in full and save it verbatim to `_figma/brief.md` (rule 2). Note its definition of done.
3. **Intake, once.** One batch of questions (the question tool: > In other tools), defaults first, only what the task
   and the profile don't answer: target (WordPress unless the task says Next.js), where to build (local folder and
   address), the Figma file and which page or frames are final, live domain and host, form recipients, tracking (GTM, or
   on WordPress the profile's tracking plugin when it names one), anything the task leaves open. A Figma link without a
   node id: ask for the page or read the file's pages with `get_metadata`. The check needs, in the project: `npm i -D
   playwright pixelmatch pngjs` (`references/qa.md`).
4. **Inventory, once** (`references/figma.md`): pages and their desktop and mobile frames, breakpoints, tokens
   (variables, or inferred from nodes), fonts, components, video, GIF, motion and prototype interactions, hidden and
   off-canvas layers (drafts are never built), assets that need edits, design gaps. Write `_figma/inventory.md`
   and `_figma/tokens.json`, then fill the progress file: `progress.py init` and one `progress.py page` per page with
   its sections in order.
5. **Plan** in `_figma/plan.md`, about 20 lines: target and stack, pages and templates, the field model in one table
   (WordPress) or the routes and components (Next.js), forms and emails, plugins or packages, design gaps and how
   each is built, decisions taken, blockers. Render and publish the progress page (`references/progress.md`).
   **All rules at the plan:** every form and where its leads go (the leads portal, or "none: <reason>"), missing
   content (marked placeholders), the live plugin checklist (WordPress), tracking, redirects, a chat or search.
   They go in the plan and the plan OK covers them, so no rule arrives mid-build and reopens finished work. A skill
   update during a task applies at the next phase boundary, never inside a QA run or a fix pass: finish it, then
   update and log the new version.
   **Recommended additions, raised at the plan** (the plan's list, and first in the plan-ready report): form
   attribution, SEO, site speed, testing, tracking; for each, what the site lacks and what we recommend, one line
   with its size ("nothing to add" is a valid line), as the table in convert-to-wordpress's
   `assets/plan/PLAN.template.md`. Form attribution is built in by default; the rest are recommendations: the
   developer decides, approved ones go into the plan, the others into the report. Anything else that changes the
   work (a risk, a blocker, a better way) is said in one line as soon as it is known, never first at done.
6. **Gate: the plan.** Show the plan in 3 lines plus the progress link and wait for the developer's OK (in a
   Command Center project: the lead's go typed in this chat, quoted in notes.md). Nothing is built before it.

## The phases

One phase at a time, in this order. Each phase ends with QA that only collects findings (below).

| Phase | WordPress | Next.js |
|---|---|---|
| 1 Setup | Local WordPress in one go, the plugins and the theme (`references/wordpress.md`); tokens, fonts and base styles from `tokens.json` | The app, Tailwind tokens from `tokens.json`, fonts with `next/font` (`references/nextjs.md`) |
| 2 Pages | Section by section (below): global parts first (header, footer, menus, mobile menu), then the template most pages share, then the other pages; every page editable in ACF; last, the long content test pages | The same order, as components and routes; content in one typed content file per page unless the task names a CMS; last, the long content route |
| 3 Forms and email | Contact Form 7 forms with the branded emails, spam protection, thank-you page; form attribution and the leads portal sender (`references/wordpress.md`) | Server actions or a route handler with validation, spam protection, the task's mail service, form attribution and the leads portal sender (`references/nextjs.md`) |
| 4 SEO, security, speed | Yoast, schema, redirects, hardening, speed checks | Metadata API, sitemap, robots, JSON-LD, headers, speed checks |
| Fix | One full QA run over every route (its findings join the list), then every open finding fixed, blockers and majors first | Same |
| QA until 0 | Each fix pass re-checked, scoped to what changed (`references/qa.md` section 10), until a re-check finds 0 | Same |
| Gate: go-live | The developer's go | Same |
| Live | Launch, then convert-to-wordpress's live plugin checklist and plugin check (`references/wordpress.md` > Live); staging gets none of the live list; live QA; report; then Duplicator deleted | Deploy where the task says; live QA; report |

Only a **blocker** is fixed at once during a phase: the site breaks, or the next phase can't start. Everything
else waits for the Fix step, so each phase runs straight through.

### The section loop (phase 2)

For every section, in page order:

1. `progress.py <dir> set <page> <section> building` and `progress.py <dir> now "<page>: <section>" --next ...`.
2. **Figma:** `get_design_context` for that section's desktop node and its mobile node only. Sparse answer:
   request its visible child nodes in one parallel batch. Save the values to `_figma/spec/<page>--<section>.md`
   (sizes, spacing, type, colours as token names, assets, interactions, copy) with the lines the check reads:
   `box@W`, `el@W` for each text style, button and image, `state@W` for each variant (`references/qa.md`). Save
   Figma's render of the node at 1x to `_figma/qa/figma/<page>--<section>@<W>.png` by its URL. Download its
   assets into the project (rule 7). A section that repeats one already built: reuse it, no new call.
3. **Build** from the spec, in the project's own stack: real layout (flex, grid), never Figma's absolute
   positions; tokens, never raw values; the copy verbatim; `data-section="<slug>"` on the section's root (the
   check script finds it there). WordPress: a template part with its ACF fields, seeded
   with the Figma copy (`references/wordpress.md`). Next.js: a component with typed props.
4. **Check your own work:** `node <kit>/scripts/check.mjs --base <url> --route <path> --page <page> --section
   <slug>` (1440 and 375: box, pixel diff, elements, states). Make your own mismatches match now: that is
   building, not the fix loop. Stop when the section passes (rule 3); open the diff image only if it fails.
5. `progress.py <dir> set <page> <section> built` (one write per section). When the page's last section is built:
   publish the progress page (`references/progress.md`: at every unit end and every stop).

Statuses: `todo` > `building` > `built` > `checked` (QA passed on it) > `fixed` (it had findings; all fixed and
re-checked). A section with an open finding shows it on the page.

## QA (after each phase, and the loop at the end)

Details: `references/qa.md`.

1. First `progress.py now "QA <phase>"` and publish (a QA run is a long step). Then `check.mjs` over the phase's
   routes (and the long content test pages from phase 2) at 1440 and 375 plus the overflow sweep (320 to 1920).
   It writes the full result to `_figma/qa/` and prints a summary. Then the code gates (rule 13): PHPCS, Prettier,
   ESLint and the self-check (`references/qa.md`).
2. One fresh read-only check (a subagent; in Claude Code on a cheaper model such as Sonnet; other tools: > In other
   tools; without subagents, a new chat told to only read): the check's numbers first, images only for its failures,
   then the phase's checklist, then a code review of the files the phase changed (`references/qa.md`). Every phase, not
   only the first ones. It changes nothing and returns findings.
3. Every finding goes into the list once: `progress.py <dir> finding add ...` (severity, page, section, what,
   expected from Figma, measured). Duplicates are merged. Nothing is fixed now, except a blocker.
4. Publish the progress page (the run's findings with their status), report the phase's stop (rule 11) and go
   straight on to the next phase. No go is needed between phases.

After phase 4: **one full QA run** over every route (findings with `--phase "qa run 1"`), then **fix passes**:
fix every open finding (`progress.py finding fix <id>` after each, with how it was verified; publish after each
fix batch), then re-check what the pass changed: each fixed item, a full read-only review of the changed files and
their callers, pixel only on the routes whose rendering changed (`references/qa.md` section 10; WordPress: the
kit's fix loop). Blockers and majors at once; a later minor outside the changed code goes in the next pass, with no
new full run. Repeat until a re-check finds 0 and none is open. Then publish the progress page, write the
pre-launch part of the report (`references/live.md` > The report), and ask for the go-live gate.

## Live and the report

After the go-live gate, read `references/live.md`: the launch per target (WordPress through convert-to-wordpress's
launch steps and its plugin list per environment, proven by its `plugin-check.py`; Next.js where the task says),
the leads portal on every lead form, live QA, and the report (`_figma/report.md`, DONE first). The developer types
every live password, licence key and API key.

## Project files (private)

Everything for the build lives in `_figma/` at the project root (WordPress root, or the Next.js repo root):
`brief.md`, `inventory.md`, `tokens.json`, `plan.md`, `spec/`, `qa/`, `progress.json`, `progress.html`,
`checkpoint.md`, `report.md`. It is never served (WordPress: an `.htaccess` with `Require all denied` inside it;
Next.js: outside `public/`) and never committed (add `_figma/` to `.gitignore`). The project's handoff files follow
the developer's handoff rules.

## Done means

Every page and section `checked` or `fixed` on the progress page; QA's last full run found 0; the code gates pass
(rule 13: PHPCS, Prettier, ESLint, the self-check, the code review); every page editable (WordPress) or every
route built from typed content (Next.js); forms, emails, form attribution and the leads portal proven on live; the
Recommended additions raised at the plan and decided; SEO, tracking and the
conversion proven on live; the live plugin checklist done and `plugin-check.py --env live` OK on a live WordPress,
then Duplicator deleted (`--done`); nothing private reachable; the
report written and the progress page republished; the stop report sent.
