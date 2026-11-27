# The start in full: intake, inventory, plan

SKILL.md > Start keeps a one-line summary of steps 3 to 5; the steps in full are here, moved unchanged in 0.4.0.
Open this file once, at the start (after the task is saved). Paths are relative to the skill folder.

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
   **All rules at the plan:** every form and where its leads go (email, CFDB7 on WordPress, a leads portal only
   when the profile names one), missing content (marked placeholders), the live plugin checklist (WordPress),
   tracking, redirects, a chat or search.
   They go in the plan and the plan OK covers them, so no rule arrives mid-build and reopens finished work. A skill
   update during a task applies at the next phase boundary, never inside a QA run or a fix pass: finish it, then
   update and log the new version.
   **Recommended additions, raised at the plan** (the plan's list, and first in the plan-ready report): form
   attribution, SEO, site speed, testing, tracking; for each, what the site lacks and what we recommend, one line
   with its size ("nothing to add" is a valid line), as the table in convert-to-wordpress's
   `assets/plan/PLAN.template.md`. Form attribution is built in by default; the rest are recommendations: the
   developer decides, approved ones go into the plan, the others into the report. Anything else that changes the
   work (a risk, a blocker, a better way) is said in one line as soon as it is known, never first at done.
