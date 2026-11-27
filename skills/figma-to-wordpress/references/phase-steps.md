# The phase steps in full

SKILL.md keeps the rules, the phase table and a short summary of each loop; the steps with their commands are here,
moved unchanged in 0.3.0, and what each phase must prove (0.4.0). Open a section when its step starts, and only that
section. Paths are relative to the skill folder.

## Contents

- The section loop (phase 2)
- QA (after each phase, and the loop at the end)
- What each phase must prove

## The section loop (phase 2)

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
4. **Check:** `node <kit>/scripts/check.mjs --base <url> --route <path> --page <page> --section
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
2. One read-only check by a reader that never saw the build (a subagent run in the background; in Claude Code on a
   cheaper model such as Sonnet; other tools: > In other tools; without subagents, a new chat with the same brief; the
   chat that built it never stands in): the check's numbers first, images only for its failures,
   then the phase's checklist, then a code review of the files the phase changed (`references/qa.md`). Every phase, not
   only the first ones. It changes nothing and returns findings.
3. Every finding goes into the list once: `progress.py <dir> finding add ...` (severity, page, section, what,
   expected from Figma, measured). Duplicates are merged. Nothing is fixed now, except a blocker.
4. Publish the progress page (the run's findings with their status), report the phase's stop (rule 11) with the
   phase's `Pass|Fail` lines (> What each phase must prove) and go straight on to the next phase. No go is needed
   between phases.

After phase 4: **one full QA run** over every route (findings with `--phase "qa run 1"`), then **fix passes**:
fix every open finding (`progress.py finding fix <id>` after each, with how it was verified; publish after each
fix batch), then re-check what the pass changed: each fixed item, a full read-only review of the changed files and
their callers, pixel only on the routes whose rendering changed (`references/qa.md` section 10; WordPress: the
kit's fix loop). Blockers and majors at once; a later minor outside the changed code goes in the next pass, with no
new full run. Repeat until a re-check finds 0 and none is open. Then publish the progress page, write the
pre-launch part of the report (`references/live.md` > The report), and ask for the go-live gate.

## What each phase must prove

At the plan gate and each phase close, report every item as `Pass|Fail | item | evidence`; the evidence (in
brackets) is the tool's output, pasted (SKILL.md rule 13); an item without it is Fail. "cwp" means that item of
convert-to-wordpress's SKILL.md > What each phase must prove (0.11.0 or later), with its evidence, never copied
here. Every phase close also carries the code gates (PHPCS 0 on WordPress, `npx prettier --check .` and ESLint 0,
each `oneoff.py` hit fixed or kept with a reason: `references/qa.md` section 7) and the read-only check's findings
logged (`progress.py status`).

- **Plan (no code):** `_figma/brief.md`, `inventory.md`, `tokens.json`, `plan.md` (ls); every page and section on
  the board (`progress.py status`); forms and where leads go, placeholders, the live plugin checklist (WordPress),
  tracking, the Recommended additions table (plan.md); the developer's OK (quoted in notes.md, `progress.py log`).
- **1 Setup:** WordPress: cwp's P1 `setup.py` and PHPCS 0 items; Next.js: `npm run build` OK, `npx tsc --noEmit` 0;
  both: the type scale and colours from `tokens.json` on a test page (check.mjs el rows), no PHP notices (debug.log)
  and no console errors (check.mjs page rows), `_figma/` 403 or outside `public/` (curl -I).
- **2 Pages:** every section `built` after `check.mjs` exit 0 at 1440 and 375 (box, pixel, el, state rows); the
  sweep 320 to 1920 and the long content pages without overflow or clipped text (check.mjs); WordPress: a field
  edit shows on its page (wp-cli or wp-admin, then curl); Next.js: every route reads its `src/content/` file
  (grep); thank-you 200 noindex, 404 page 404 (curl -I).
- **3 Forms and email:** WordPress: cwp's P3 items; Next.js: every form answers with the thank-you redirect (curl),
  the email in the local mail capture, honeypot and the task's spam protection (the markup); both: a post from a
  page with UTMs and a click id shows them in the Lead source table (mail capture), `/thank-you` pushes one
  `generate_lead` (the browser's dataLayer); a leads portal sender only when the profile names one (the code).
- **4 SEO, security, speed:** title, description, canonical, one H1, alt and `lang` with 0 failing rows, the LCP
  image not lazy (check.mjs page rows); sitemap and robots 200, `/thank-you` noindex, private files 403 or outside
  `public/`, security headers (curl -I); each `application/ld+json` block parses (JSON.parse); local Lighthouse
  scores (as measured, a regression guard).
- **Fix and QA loop:** one full run logged (`--phase "qa run 1"`); the last re-check found 0, none open, every
  section `checked` or `fixed` (`progress.py status`); the report's pre-launch part (`_figma/report.md`);
  **Go-live:** the developer's go (quoted in notes.md, `progress.py log`).
- **Live:** WordPress: cwp's P6 Launch and P6 Live QA items (`plugin-check.py --env live`, `live-qa.py`, track.mjs,
  PageSpeed Insights, the test leads), then Duplicator deleted (`plugin-check.py --done`); Next.js: the live address
  200 (curl -I), `check.mjs --base <live url>` exit 0, one test lead per form (the developer's confirmation),
  `generate_lead` fires (the browser's dataLayer), PageSpeed Insights mobile and desktop (scores as measured); both:
  `_figma/`, private files and the long content pages not reachable (curl -I), `_figma/report.md` with DONE first,
  the progress page republished (its URL).
