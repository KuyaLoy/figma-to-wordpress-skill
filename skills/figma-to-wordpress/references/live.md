# Live: the launch, the leads portal, live QA and the report

Read this after the developer's go-live gate (SKILL.md > Live and the report). Before the gate, the pre-launch part
of the report uses > The report.

## The launch per target

- **WordPress:** follow convert-to-wordpress's launch steps (backup, package, move, checks, rollback) and its plugin
  list per environment, the one list (`references/wordpress.md` > Live): live gets exactly that list, staging the
  three core plugins and none of the live list; its `plugin-check.py` proves it. After live QA is at 0 and the
  report is done, Duplicator is deleted (`--done --files`). The developer types every live password and licence
  key.
- **Next.js:** deploy where the task says (Vercel unless it names a host); environment variables typed by the
  developer in the host's settings; the domain and redirects as the task says.
- **Leads portal** (both targets): mandatory on a live site with a lead form; the code is in from phase 3, the
  endpoint and key go in on live only (typed by the developer; WordPress: Theme Settings > Leads portal, Next.js:
  the host's environment variables), the GET check passes before the switch. A site
  without a lead form says so in the plan. The portal's address comes from the developer's profile or the task.
- **Live QA:** `check.mjs` on the live address over every route; forms with one real test lead each, named
  `TEST <developer> - please ignore`, after the developer agrees, each reaching the email and the leads portal
  (its admin shows the count per form); one of them sent from a page opened with
  `?utm_source=qa&utm_medium=test&utm_campaign=launch&gclid=TEST` shows them in the email's Lead source table
  and in the portal; tracking and the conversion (`generate_lead`) fire; nothing from
  local left (search engines allowed, debug off, no `_figma/` or private files reachable, the long content test
  pages removed: `references/qa.md`).

## The report

`_figma/report.md`, standing alone: **DONE** first; what was built (pages, sections, forms); how it was verified
(QA rounds, final 0, routes and widths checked, the pass marks used, live checks); what is not verified; decisions
and defaults taken;
design gaps built from the design system; image edits made; what the client must supply or do (copy marked TBC,
DNS, logins); rollback location; "Findings (not touched)". A Zoho task gets a short completion comment draft for the
developer or Command Center to post; this skill never posts in Zoho itself.
