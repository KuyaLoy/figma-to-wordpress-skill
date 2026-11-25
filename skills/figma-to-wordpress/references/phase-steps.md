# The phase steps in full

SKILL.md keeps the rules, the phase table and a short summary of each loop; the steps with their commands are here,
moved unchanged in 0.3.0. Open a section when its step starts, and only that section. Paths are relative to the
skill folder.

## Contents

- The section loop (phase 2)
- QA (after each phase, and the loop at the end)

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
