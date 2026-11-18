---
name: figma-to-wordpress
description: Builds a Figma design 1:1 as a WordPress site (every page editable in ACF PRO, forms in Contact Form 7, Yoast SEO) or as a Next.js site (App Router, TypeScript, Tailwind), in one chat. The task's instructions come first, the design is inventoried once, then the build runs phase by phase (setup, pages section by section, forms and email, SEO, security and speed) with QA that only collects findings, one fix loop until QA finds 0, the developer's go, then live. A progress page shows what is done and what is not. Use whenever a Figma file or link has to become a website.
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
| `references/qa.md` | QA per phase, the check script, the read-only check, the fix loop | End of each phase |
| `references/progress.md` | progress.json and the progress page | Start; when publishing |
| `scripts/progress.py` | Pages, sections, statuses, findings, log; renders the progress page | Every section |
| `scripts/check.mjs` | Browser check at 1440 and 375 plus an overflow sweep; summary only | Every section, every phase |

WordPress builds also use the **convert-to-wordpress** skill's kit (setup scripts, theme, fields, forms, SEO,
launch): `references/wordpress.md` says which parts and where to find it. Never copy its rules here; read them there.

## Rules (always)

1. **One chat builds the whole site.** No builder, tester or QA chats, no helper subagents for building. The only
   other agent is the read-only QA check at the end of each phase. (Learned 18 Nov 2026: a six-chat build spent 79%
   of its usage on chats re-reading their own history.)
2. **The task first.** A Zoho (or other tracker) task's instructions win over this skill's defaults. Read all of
   it (description, linked docs, comments, attachments) before the inventory and save it verbatim to
   `_figma/brief.md`. Follow it verbatim: copy, icons, emoji, long titles, no rewording.
3. **1:1 from real values.** Build from Figma's data (`get_design_context`, variables), never by eye from a
   screenshot; screenshots are only the visual target to compare against. Done standard at the designed widths
   (usually 1440 and 375): every section within 1 px of Figma on desktop and 2 px on mobile. Between and beyond them
   nothing overflows, is cut, squashed or stretched. A mismatch is accepted only with numeric proof that Figma
   itself is inconsistent; log it as a decision.
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
   score. A heavy design (video, big imagery, motion) gets a speed plugin on WordPress (`references/wordpress.md`).
7. **Assets exactly as in Figma.** Every image and SVG exported from Figma into the project, in its exact slot, at
   2x for raster images (sharp at DPR 2), people never cut by a crop. No temporary Figma asset URLs left in code.
   Edits a Figma export can't give (background removal, extending an image) only with a tool the developer has,
   true to the source, and listed in the report.
8. **Secrets stay out.** No password, licence key or API key in the repo, the theme, `_figma/`, the progress page or
   any report. The local default admin login comes from the developer's local profile at run time and is for local
   sites only; live passwords, licence keys and API keys are typed by the developer.
9. **Live only after the developer's go.** A backup before any live change, one change at a time, a rollback named.
10. **Spend less.** Scripts write big output to disk and print a summary. Read summaries, not whole files. Never read
    node_modules, vendor, minified, lock or build files. Screenshots only of failures, cropped to the problem.
11. **Never stop silently.** Every turn that ends without the work going on (plan ready, a phase's QA done, a
    checkpoint, a block, waiting for a go) ends with a short stop report: what was done, the state, decisions taken,
    and last `Next: <step> — waiting on <who>`. In a Command Center project send it to Command Center (parent) too.
12. **Context watch.** Check your context % before each section. From 50%: finish the section, write
    `_figma/checkpoint.md` (task, go quoted, done so far, state, exact next step), send CHECKPOINT and end the turn.
    At 75%: the same at the first safe point. `progress.json` and the checkpoint are enough to resume cold.

In a Command Center project (handoff.md says `Mode: Command Center`) this chat is a task chat: its Worker rules
apply as well (go quoted in notes.md, stop messages, no Zoho posts). Where they and this skill differ, they win.

## Start

1. **Resuming?** If `_figma/` exists: read `_figma/checkpoint.md` (if any) and run `python3 <kit>/scripts/progress.py
   <project>/_figma status`. Re-check the real state (files, site) against it, then continue from its next step.
2. **The task.** Read it in full and save it verbatim to `_figma/brief.md` (rule 2). Note its definition of done.
3. **Intake, once.** One batch of questions, defaults first, only what the task and the profile don't answer:
   target (WordPress unless the task says Next.js), where to build (local folder and address), the Figma file and
   which page or frames are final, live domain and host, form recipients, tracking (GTM), anything the task leaves
   open. A Figma link without a node id: ask for the page or read the file's pages with `get_metadata`.
4. **Inventory, once** (`references/figma.md`): pages and their desktop and mobile frames, breakpoints, tokens
   (variables, or inferred from nodes), fonts, components, video, GIF, motion and prototype interactions, hidden and
   off-canvas layers (drafts are never built), assets that need edits, design gaps. Write `_figma/inventory.md`
   and `_figma/tokens.json`, then fill the progress file: `progress.py init` and one `progress.py page` per page with
   its sections in order.
5. **Plan** in `_figma/plan.md`, about 20 lines: target and stack, pages and templates, the field model in one table
   (WordPress) or the routes and components (Next.js), forms and emails, plugins or packages, design gaps and how
   each is built, decisions taken, blockers. Render and publish the progress page (`references/progress.md`).
6. **Gate: the plan.** Show the plan in 3 lines plus the progress link and wait for the developer's OK (in a
   Command Center project: the lead's go typed in this chat, quoted in notes.md). Nothing is built before it.

## The phases

One phase at a time, in this order. Each phase ends with QA that only collects findings (below).

| Phase | WordPress | Next.js |
|---|---|---|
| 1 Setup | Local WordPress in one go, the plugins and the theme (`references/wordpress.md`); tokens, fonts and base styles from `tokens.json` | The app, Tailwind tokens from `tokens.json`, fonts with `next/font` (`references/nextjs.md`) |
| 2 Pages | Section by section (below): global parts first (header, footer, menus, mobile menu), then the template most pages share, then the other pages; every page editable in ACF | The same order, as components and routes; content in one typed content file per page unless the task names a CMS |
| 3 Forms and email | Contact Form 7 forms with the branded emails, spam protection, thank-you page | Server actions or a route handler with validation, spam protection and the task's mail service |
| 4 SEO, security, speed | Yoast, schema, redirects, hardening, speed checks | Metadata API, sitemap, robots, JSON-LD, headers, speed checks |
| Fix | Every open finding in the list, one by one | Same |
| QA until 0 | Full QA over every route; new findings go to the list; fix and run again until it finds 0 | Same |
| Gate: go-live | The developer's go | Same |
| Live | Launch, then on live: a WebP conversion plugin and Contact Form CFDB7; live QA; report | Deploy where the task says; live QA; report |

Only a **blocker** is fixed at once during a phase: the site breaks, or the next phase can't start. Everything
else waits for the Fix step, so each phase runs straight through.

### The section loop (phase 2)

For every section, in page order:

1. `progress.py <dir> set <page> <section> building`.
2. **Figma:** `get_design_context` for that section's desktop node and its mobile node only, with a screenshot.
   Sparse answer: request its visible child nodes in one parallel batch. Save the values to
   `_figma/spec/<page>--<section>.md` (sizes, spacing, type, colours as token names, assets, interactions, copy).
   Download its assets into the project (rule 7). A section that repeats one already built: reuse it, no new call.
3. **Build** from the spec, in the project's own stack: real layout (flex, grid), never Figma's absolute
   positions; tokens, never raw values; the copy verbatim; `data-section="<slug>"` on the section's root (the
   check script finds it there). WordPress: a template part with its ACF fields, seeded
   with the Figma copy (`references/wordpress.md`). Next.js: a component with typed props.
4. **Check your own work:** `node <kit>/scripts/check.mjs --base <url> --route <path> --section <id>
   --spec _figma/spec/<page>--<section>.md` at 1440 and 375. Make your own mismatches match now: that is building,
   not the fix loop. Stop when the section is within the done standard (rule 3).
5. `progress.py <dir> set <page> <section> built`, then republish the progress page. One write per section.

Statuses: `todo` > `building` > `built` > `checked` (QA passed on it) > `fixed` (it had findings; all fixed and
re-checked). A section with an open finding shows it on the page.

## QA (after each phase, and the loop at the end)

Details: `references/qa.md`.

1. `check.mjs` over the phase's routes at 1440 and 375 plus the overflow sweep (320 to 1920). It writes the full
   result to `_figma/qa/` and prints a summary.
2. One read-only check by a subagent on a cheaper model (Sonnet): the phase's checklist from `references/qa.md`,
   the Figma screenshots against the local screenshots `check.mjs` saved. It changes nothing and returns findings.
3. Every finding goes into the list once: `progress.py <dir> finding add ...` (severity, page, section, what,
   expected from Figma, measured). Duplicates are merged. Nothing is fixed now, except a blocker.
4. Report the phase's stop (rule 11) and go straight on to the next phase. No go is needed between phases.

After phase 4: **Fix** every open finding (`progress.py finding fix <id>` after each, with how it was verified),
then run **full QA** over every route. New findings: add, fix, run again. Repeat until QA finds 0. Then render the
progress page, write the pre-launch part of the report, and ask for the go-live gate.

## Live

- **WordPress:** follow convert-to-wordpress's launch steps (backup, package, move, checks, rollback). On live, and
  only there: a WebP conversion plugin and Contact Form CFDB7 (form entries), plus the live plugins its essentials
  name. The developer types every live password and licence key.
- **Next.js:** deploy where the task says (Vercel unless it names a host); environment variables typed by the
  developer in the host's settings; the domain and redirects as the task says.
- **Live QA:** `check.mjs` on the live address over every route; forms with one real test lead each, named
  `TEST <developer> - please ignore`, after the developer agrees; tracking and the conversion fire; nothing from
  local left (search engines allowed, debug off, no `_figma/` or private files reachable).

## The report

`_figma/report.md`, standing alone: **DONE** first; what was built (pages, sections, forms); how it was verified
(QA rounds, final 0, routes and widths checked, live checks); what is not verified; decisions and defaults taken;
design gaps built from the design system; image edits made; what the client must supply or do (copy marked TBC,
DNS, logins); rollback location; "Findings (not touched)". A Zoho task gets a short completion comment draft for the
developer or Command Center to post; this skill never posts in Zoho itself.

## Project files (private)

Everything for the build lives in `_figma/` at the project root (WordPress root, or the Next.js repo root):
`brief.md`, `inventory.md`, `tokens.json`, `plan.md`, `spec/`, `qa/`, `progress.json`, `progress.html`,
`checkpoint.md`, `report.md`. It is never served (WordPress: an `.htaccess` with `Require all denied` inside it;
Next.js: outside `public/`) and never committed (add `_figma/` to `.gitignore`). The project's handoff files follow
the developer's handoff rules.

## Done means

Every page and section `checked` or `fixed` on the progress page; QA's last full run found 0; every page editable
(WordPress) or every route built from typed content (Next.js); forms and emails proven on live; SEO, tracking and
the conversion proven on live; WebP plugin and CFDB7 active on a live WordPress; nothing private reachable; the
report written and the progress page republished; the stop report sent.
