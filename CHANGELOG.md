# Changelog

Every change to the skill, newest first. Versions follow [Semantic Versioning](https://semver.org); the format
follows [Keep a Changelog](https://keepachangelog.com).

## [Unreleased]

## [0.5.0] - 2026-11-27

Lean tool output: long command output goes to a log, the chat gets the result line and the failures (the same idea
as convert-to-wordpress 0.13.0 rule 18). No rule, phase or check removed.

### Added

- SKILL.md > Long output (always), after the rules: output over about 50 lines goes to `_figma/logs/<step>.log`; the
  chat and every report get the command, its result line, the failures and the log path, as `check.mjs` does with
  `_figma/qa/`. Rules 1 to 13, the phase table and "Done means" unchanged.
- `references/qa.md` section 11 "Long output to a log (every command)": which commands log, the bash and Windows
  PowerShell 5.1 forms (`Out-File -Encoding utf8`), a WordPress build may use the kit's `_plan/logs/` instead, what
  the chat and reports quote, the compact flags (npm, Playwright `--reporter=line`, Prettier `--log-level warn`,
  PHPCS `-q --report=summary`, composer, `git status --porcelain`, Lighthouse JSON to a log), logs private (inside
  `_figma/`) and never holding a secret. The section index line names section 11.
- `references/other-tools.md`: the "In other tools" bullets, moved word for word from SKILL.md (which keeps the
  section, its intro and a pointer, and lists the file in the kit table). SKILL.md 18,218 B (was 18,579).
- `tests/test_lean_output_050.py`; `tests/test_token_diet_040.py` lists the 0.3.2 reference lines changed on
  purpose (CHANGED_REFS_050).

### Changed

- `references/qa.md` section 1: the check's install with `--no-audit --no-fund --loglevel=error`; section 7: PHPCS
  runs `vendor/bin/phpcs -q --report=summary`, the full report to `_figma/logs/phpcs.log` only when it finds
  something.
- `references/nextjs.md` > Speed: `npm run build > _figma/logs/build.log 2>&1`, the chat gets the result line and
  any warning.
- `references/phase-steps.md` > What each phase must prove, 1 Setup: `npm run build` OK as its result line, the log
  in `_figma/logs/build.log`.

## [0.4.1] - 2026-11-27

The company attribution standard and the agency badge from convert-to-wordpress 0.12.0, for both targets.

### Added

- SKILL.md > Every site, whatever the design shows: the footer and both emails (lead email and auto-reply) carry
  the agency badge with its link, dynamic, hidden only on the client's recorded request; every lead email has the
  eleven labelled attribution fields. Rules 1 to 13, the phase table and "Done means" unchanged.
- WordPress (`references/wordpress.md`): pointers, nothing copied, to the kit's `references/build.md` > Agency
  badge (phase 2: the footer's bottom bar, even when Figma has none; a known diff in the footer's pixel check),
  `references/forms-email.md` > Where the lead came from (the eleven fields in the Lead Attribution table, CFDB7
  and the app the profile's connector plugin feeds), > Form layout and > The auto-reply and the agency badge (its
  self-check class `branding` and `live-qa.py` check 11).
- Next.js (`references/nextjs.md`): the footer badge from `agencyBadge` in `src/content/site.ts` (image, link,
  alt; `hide` only with the client's recorded request); the lead email and the auto-reply in one branded template,
  both ending with the badge (PNG at 2x); no CRM or app connection for Next.js builds yet.
- `tests/test_attribution_041.py`.

### Changed

- Next.js form attribution follows the company standard: the eleven labels in order, `utm_id`, `gad_campaignid`
  and their first-visit fields, landing pages with their query (no value holding an "@"), the new caps, the two
  dates in the site's time zone, and the lead email's Lead Attribution table (was the 0.9.10 Lead source table).
- The phase proof (`references/phase-steps.md`), the QA checklists (`references/qa.md`) and live QA
  (`references/live.md`): a post from `?gad_campaignid=123&gclid=TEST&utm_source=google` shows the eleven rows in
  order, a plain post "Direct" and "none" rows, and the badge in the footer and both emails.
- `tests/test_token_diet_040.py`: the 0.3.2 lines changed on purpose in 0.4.1 are listed.

## [0.4.0] - 2026-11-27

Fewer tokens per build, with every rule, phase, test and QA step kept, as in convert-to-wordpress 0.11.0. Rules 1
to 13, the phase table and "Done means" are word for word as before.

### Added

- **What each phase must prove** (`references/phase-steps.md`): the plan, each phase, the fix loop and live as
  objective items, each naming the tool that gives its evidence (`progress.py status`, `check.mjs` rows, curl -I,
  the mail capture, the dataLayer, PageSpeed Insights). At the plan gate and every phase close the stop report
  carries each item as `Pass|Fail | item | evidence`; an item without evidence is Fail. On WordPress, items that
  convert-to-wordpress already proves point to its SKILL.md > What each phase must prove (0.11.0 or later),
  never copied.
- `references/start.md`: Start steps 3 to 5 (intake, inventory, plan) in full, moved word for word from SKILL.md,
  which keeps a one-line summary of each and the pointer. Read once, at the start.
- `tests/test_token_diet_040.py`: no self-check lines, the Pass|Fail items with their evidence, the fresh reader,
  the self-check named not restated, the start steps moved word for word, and nothing lost since 0.3.2 (every line
  and heading of SKILL.md and the references, rules, the phase table and "Done means" word for word).

### Changed

- **The read-only QA check** is a reader that never saw the build: a subagent run in the background, else a new
  chat with the same brief; the chat that built it never stands in (SKILL.md > QA, `references/qa.md` section 6,
  `references/phase-steps.md` > QA).
- **The self-check is named, not restated:** `references/qa.md` section 7's four grep lines become one line
  pointing to `scripts/oneoff.py`, whose header now lists its searches; `tests/test_oneoff.py` still runs the four
  grep lines against it.
- SKILL.md 19,962 -> 18,209 bytes (room under the 20,000 limit); `tests/test_slim_030.py` lists the lines changed
  on purpose.

### Removed

- The "check your own work" framing (it makes the agent over-check, at more tokens and no better result): SKILL.md
  > The section loop and `references/phase-steps.md` step 4 now just run `check.mjs` until it passes. The real
  checks stay: `check.mjs`, the code gates, QA and the tests.

## [0.3.2] - 2026-11-27

### Changed

- **The leads portal is optional, none by default,** as in convert-to-wordpress 0.10.2 (its
  `references/forms-email.md` > The leads portal; nothing copied): built, set up and checked only when the profile
  names one. Without one, leads go by email (with the Lead source table) and, on WordPress, Contact Form CFDB7 on
  live, with no blocker and no portal step. SKILL.md (plan, phase 3, Live, Done means), `references/live.md`,
  `references/wordpress.md`, `references/nextjs.md` and `references/qa.md` say so.
- `tests/test_slim_030.py` lists the SKILL.md lines 0.3.2 changed on purpose.

## [0.3.1] - 2026-11-25

### Changed

- **WordPress** (`references/wordpress.md` > Phase 3): where leads are stored points to convert-to-wordpress's
  rule 17 (Leads: CFDB7 only) and its `references/forms-email.md` > Where leads are stored: CFDB7 only (0.10.1 or
  later), and to its self-check's `lead-storage` finding; nothing copied.
- **Next.js** (`references/nextjs.md` > Phase 3): one line, leads go only to the email and the leads portal, never
  to a database of the build's own.

## [0.3.0] - 2026-11-25

A slimmer SKILL.md: less to load in every chat, every rule kept.

### Changed

- **SKILL.md** about 4,950 tokens, 19,800 characters (was about 5,600): the section loop's five steps and the QA steps moved,
  word for word, to the new `references/phase-steps.md`; SKILL.md keeps the rules word for word, the phase table,
  the statuses and a short summary of each loop with an "open when" pointer.
- **`references/wordpress.md`:** setup and launch point to convert-to-wordpress's `references/phase-steps.md` >
  P1 Setup and > P6 Launch (0.10.0 or later) instead of its SKILL.md.

### Added

- `tests/test_slim_030.py`: nothing lost from the 0.2.15 SKILL.md (every heading and line is still in SKILL.md or
  a reference), the rules unchanged, the pointers resolve, SKILL.md under 20,000 characters and 250 lines.

## [0.2.15] - 2026-11-25

### Changed

- **SKILL.md > In other tools:** browser steps in Antigravity drive the lead's Chrome through the chrome-devtools
  MCP, as convert-to-wordpress's `references/agents.md` > Per tool says (0.9.16 or later, with its tab rules); the
  built-in browser pane only as a fallback.
- **`references/wordpress.md` > Live:** the package step points to convert-to-wordpress 0.9.13 or later, whose
  filters and package check already leave out `_figma/`; the step that added it by hand is gone.

## [0.2.14] - 2026-11-24

Runs the same in Codex, Antigravity and T3 Code as in Claude Code (a cross-tool audit). Claude's steps are unchanged.

### Added

- **SKILL.md > In other tools:** where a step names a Claude tool, convert-to-wordpress's `references/agents.md` >
  Per tool (0.9.14 or later), plus this skill's own: the Figma MCP server, asking, the read-only QA subagent
  (Codex `spawn_agent`, Antigravity `invoke_subagent`), the progress page as a local file, the context meter,
  `py -3` on Windows.
- **`progress.py render --refresh N --open`** (the same flags as convert-to-wordpress's `render.py`): the local
  page opens once and reloads itself every N seconds; the setting is kept in progress.json (`refresh`), so every
  later write keeps it. Tested.
- **`scripts/oneoff.py`:** the self-check searches in Python, for any shell (also .jsx and .tsx, `.next` skipped);
  a test proves the same hits as the grep lines in `references/qa.md`.
- **`references/figma.md` > In other tools:** connecting the Figma MCP server per tool; not connected is a blocker.

### Changed

- The description carries the trigger words people type ("build this Figma design", "Figma to WordPress",
  "Figma to Next.js"...).
- SKILL.md under 250 lines: the Live details and the report moved, word for word, to the new `references/live.md`
  (read at the go-live gate); rule 11's title states point to `references/progress.md` > Publishing.
- `references/qa.md`: which section to open when; the Figma render download also in PowerShell and Python; the
  read-only check per tool; the node-ID search also reads .jsx.
- `references/wordpress.md`: the kit's folder in other tools.

## [0.2.13] - 2026-11-24

WordPress builds point to convert-to-wordpress 0.9.12 (from a real build's retro). Next.js is unchanged apart
from one line.

### Changed

- **WordPress** (`references/wordpress.md`), pointing to the kit, never copying it:
  - The leads portal's address and password always in Theme Settings > Leads portal (administrators only, seeded
    empty, pasted on live; wp-config constants win when defined); live checks with `leads-check.py --site`.
  - Theme Settings tabs across the top (the kit's default) and the kit's Leads portal group kept.
  - Duplicator Pro installed in setup from the profile's `plugin_zips.duplicator_pro` when set.
  - The package leaves out the kit's private and agent files; `_figma/` is added to the filters by hand and must not
    be in the archive's listing; the package check is reported with its output (`package.py --check-zip`).
  - Staging after a Duplicator import: the kit's must-use environment file and `acf-json/.htaccess`; the
    environment and `live-qa.py --hidden` checked.
- **SKILL.md** rule 13: kit files copied with the prefix swap only (changes listed with why); a check is reported
  only with its output. Live: where the portal settings go per target.
- **Next.js** (`references/nextjs.md`): one line, the portal settings stay environment variables.

## [0.2.12] - 2026-11-23

The default plugin stack per environment, as convert-to-wordpress 0.9.11. Next.js is unchanged.

### Changed

- **WordPress** (`references/wordpress.md`): points to the kit's plugin list per environment (its
  `references/wordpress-essentials.md` > Plugins) instead of naming plugins here. Phase 1 installs only the local
  list: the profile's `"where": "live"` plugins and the live-only ones never go on local or staging. Live has
  exactly the kit's list, nothing else unless the task asks; staging the three core plugins (Redirection if needed).
- Every live redirect in the Redirection plugin; reCAPTCHA and the leads portal on every live form.
- Tracking: when the profile names a tracking plugin, it is the only way: no ACF tracking fields and no GTM in the
  theme. The kit's self-check runs with `--profile`, which flags both.
- Live QA runs the kit's `plugin-check.py --env live`; after live QA is at 0 and the report is done, Duplicator is
  deleted and `--done --files` confirms it. SKILL.md intake, phase table, Live and Done means say so.

## [0.2.11] - 2026-11-23

The lead email's "Lead source" table, as convert-to-wordpress 0.9.10 (the layout of an existing company build).

### Changed

- **Next.js** (`references/nextjs.md` phase 3): the lead email's "Where this lead came from" row becomes the Lead
  source table (HTML and plain text): a title row on the brand colour with the higher-contrast text (#28292D with
  white without one), "First visit", "Latest campaign visit" (only when it differs), "Form sent from"; each visit's
  source in words ("Google Ads click", "Google search", "Direct (typed in, bookmark or no source)"...), then
  Campaign, Keyword, Ad, the click ids, From, Landing page, "When: ... UTC"; "Not recorded" without page-script
  data. The browser keeps the first visit and the latest campaign visit.
- New fields, as the kit: `first_term`, `first_content`, `first_gclid`, `first_gbraid`, `first_wbraid`,
  `first_fbclid`, `first_msclkid` (200) and `last_seen`; `first_seen` and `last_seen` are "YYYY-MM-DD HH:MM" UTC
  (16). `sendLead()` sends them under the same names.
- **WordPress** (`references/wordpress.md`): points to the kit's 0.9.10 rule (the Lead source table, its title row
  in `KITWP_BRAND_COLOUR`) and its must-use plugin for a WordPress site the kit did not build.
- QA forms row and Live QA name the Lead source table.

## [0.2.10] - 2026-11-23

Form attribution on every lead form by default, and the Recommended additions raised at the plan (as
convert-to-wordpress 0.9.9).

### Added

- **Form attribution, both targets,** with convert-to-wordpress 0.9.9's names: last touch (`utm_source`,
  `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`, `gclid`, `gbraid`, `wbraid`, `fbclid`, `msclkid`,
  `landing_page`, `referrer`) and first touch (`first_source`, `first_medium`, `first_campaign`,
  `first_landing_page`, `first_referrer`, `first_seen`) in hidden fields; server caps (500 for the addresses, 10 for
  the date, 200 for the rest); the lead email's "Where this lead came from" row ("Direct" when none); the portal
  fields; `generate_lead` with `form_name`, `lead_source`, `lead_medium` on the thank-you page.
  - WordPress: `references/wordpress.md` points to the kit's rule (its forms-email.md > Where the lead came from).
  - Next.js: `references/nextjs.md` phase 3 spells out the same capture (consent as the kit's "auto": Google
    Consent Mode), the server-only checks, the email row, the conversion, and the fields in `sendLead()`.
- **Recommended additions at the plan:** form attribution, SEO, site speed, testing, tracking, one line each with
  its size, first in the plan-ready report; the developer decides. Anything that changes the work is said as soon as
  it is known (SKILL.md plan step).
- Live QA and the QA forms checklist: a test lead from a page with UTMs and a click id shows them in the email and
  the portal; a plain one shows "Direct".

## [0.2.9] - 2026-11-20

The chat's state shows in its title, so the sidebar shows what is working (as convert-to-wordpress 0.9.8).

### Added

- **State in the title** (Claude desktop app; other tools skip it): `▶ RUNNING | <title>`, `⏸ WAITING on <who> |
  <title>`, `✋ BLOCKED | <title>`, `✓ DONE | <title>`, set with `set_session_title` "self", one call per state
  change, next to the RUNNING line (SKILL.md rule 11, references/progress.md > Publishing).

## [0.2.8] - 2026-11-20

A chat that ends its turn while its own work runs says so, so it never looks stopped (as convert-to-wordpress
0.9.7).

### Added

- **Running, not stopped:** while a background command, a subagent or a check runs past the end of a turn, the
  last message's first line, the recap and the progress page's Now line read `RUNNING, not stopped: <what>, started
  HH:MM; I continue by myself when it finishes.`; a real stop says what it waits on instead (SKILL.md rule 11,
  references/progress.md > Publishing).

## [0.2.7] - 2026-11-20

The retro of a large conversion build: faster, with the same quality bar.

### Added

- The live progress page (Claude): `scripts/live.py`, the same code and the same database collections and fields as
  convert-to-wordpress 0.9.6 (`meta/now`, `phases/<id>`, `items/<page>--<section>`, `findings/<id>`,
  `log/L<hash>`). Every render also writes `progress-live.html` (published once, privately, with the database) and
  `progress-rows.json` (ArtifactData batches of at most 50, `existing` documents need `if_version`);
  `progress.py <dir> render --pushed` records them; `progress.py <dir> url <link> --live` saves its link. The open
  page updates itself. progress.json stays the source; the static page stays for other tools.
- `references/wordpress.md` > QA: points to convert-to-wordpress 0.9.6's pre-QA self-check and its fix loop.

### Changed

- QA converges (`references/qa.md` section 10, both outputs): one full QA run per site; then fix passes, each
  re-checking every fixed item, a full review of the changed files and their callers, and pixel only on the routes
  whose rendering changed; blockers and majors at once; a later minor outside the changed code goes in the next pass
  with no new full run; a new full run only when a change touched most of the site. Every line is reviewed in full
  once and again whenever it changes.
- All rules at the plan: forms and where leads go, placeholders, the live checklist, tracking, redirects; a skill
  update during a task applies at the next phase boundary.
- Shorter resumes: checkpoint at a page or phase end where the thresholds allow, with the exact next step; a resume
  re-checks only what can have changed.
- progress.json: one addition, `live_url`. A file made before still loads and renders.

## [0.2.6] - 2026-11-20

### Changed

- The progress page shows what is happening and stays current, the same page and keys as convert-to-wordpress
  0.9.5: at the top, in large type, Now (the step and the time it started), Next, anything waiting or blocked, and
  the time the page was rendered ("n min ago" from one tiny inline script). New command
  `progress.py <dir> now "<step>" [--next ...] [--waiting ...] [--blocked ...]`.
- Every QA finding is listed with its status (open, fixed, decided), with counts per status and per QA run (the
  finding's `phase`; in the QA-until-0 loop `--phase "qa run <n>"`), open first, fixed and decided folded with
  how each was fixed or why it was kept.
- Publishing: at every unit end (the plan, each page built, each QA run collected, each fix batch, QA at 0, live)
  and every stop, and before a long step (write `now`, publish, then start); the same link as before. Replaces
  "only at the plan, once per finished page and at each phase end".
- progress.json: additions only, `now` (`step`, `started`), `next`, `waiting`, `blocked`; `updated` is the time of
  the last write or render. A file made before 0.2.6 still loads and renders. `render` now saves the update time.

## [0.2.5] - 2026-11-20

### Added

- The leads portal, mandatory on a live site with a lead form (a site without one says so in the plan): each lead
  is also posted to the portal whether the email went out or failed; the code is in from phase 3, the endpoint and
  key go in on live only, a GET check (stores nothing) proves them before the switch, then one TEST lead per form.
  The portal's address comes from the developer's profile or the task, never from the skill.
- WordPress: `references/wordpress.md` points to convert-to-wordpress 0.9.4's rule (its `references/forms-email.md`
  > The leads portal) in phase 3, and the live checklist summary names its leads portal item and `leads-check.py`.
- Next.js: `references/nextjs.md` phase 3 adds a server-only `sendLead()` (`form`, `idempotency_key`, the fields,
  `source_url`, `ip_address`, `gclid`, `fbp`, `fbc`; Bearer key; 5 second timeout; 200 and 202 delivered; a failure
  logged with the status only, never blocking the visitor), off unless `LEADS_ENDPOINT` and `LEADS_WRITE_KEY` are
  set, which they are only for Production on the host. Live: the GET check, then one TEST lead per form.
- SKILL.md: the phase 3 row, a Leads portal item under Live, Live QA (each test lead reaches the email and the
  portal) and "Done means".

## [0.2.4] - 2026-11-20

### Changed

- The cache plugin, as convert-to-wordpress: every live WordPress site gets the live checklist's cache plugin
  (LiteSpeed Cache unless the profile's `cache_plugin` names another), never locally or on staging. A heavy design
  only uses more of its options on live (page and browser cache first, then CSS and JS one at a time, each with a
  parity check), never a second speed plugin. SKILL.md rule 6 and `references/wordpress.md` > Phase 4, pointing to
  the kit's `references/seo-security.md` > Performance.

## [0.2.3] - 2026-11-20

### Changed

- Live: the WordPress rules are the same as convert-to-wordpress's, so the skill points to its live plugin checklist,
  the one list (its `assets/launch/RUNBOOK.template.md` section 4 and `references/launch.md` > After the installer),
  instead of naming "a WebP conversion plugin and Contact Form CFDB7": the profile's live plugins from the
  developer's plugin folder (versions checked before go-live), Contact Form CFDB7, Converter for Media, the
  reCAPTCHA v3 keys and the cache plugin (LiteSpeed Cache by default). Staging gets none of it. SKILL.md's Live row,
  Live section and "Done means", and `references/wordpress.md` > Live.
- `references/wordpress.md` step 4: ACF PRO is activated by the profile's `acf_pro_license`, written only into local
  wp-config files by the kit's `make-wp-config.py`, not pasted by the developer.

## [0.2.2] - 2026-11-19

Starter rule and code quality, from a read-only audit of a large Figma build (no bugs, but about 2,000 one-off
values, a copied colour map, an oversized section, node IDs and ticket tags in comments, unused kit files, PHPCS
passing through ignore comments, code review only in early phases).

### Changed

- `references/wordpress.md`: the starter by rule, not "_tw by default". Clearly easier in Tailwind (a design system
  with repeating tokens, many reusable sections): _tw. A normal site that doesn't really need Tailwind: Barebones
  with CSS-variable tokens. A Figma design is never a Tailwind source. The plan states the choice and one reason.
- QA: the read-only check also reviews the code each phase changed, at every phase gate.

### Added

- SKILL.md rule 13, clean code: tokens not one-offs, ship only what is used, comments say why (no Figma node IDs or
  ticket tags), size limits (about 15 options or 250 lines; one job per file; no inline JS), gates (PHPCS with the
  theme's escaping helpers registered, Prettier, ESLint, the self-check) at every phase gate and before DONE.
- `references/qa.md` section 7: the code gates and four self-check greps (one-off values, hex outside the tokens
  file, node IDs and ticket tags, ignore comments); a code checklist for every phase.
- `references/nextjs.md`: no arbitrary values, Prettier with the Tailwind plugin, unused starter files removed.

## [0.2.1] - 2026-11-18

### Fixed

- Long content on WordPress: `references/qa.md` now names convert-to-wordpress 0.9's `long-content.php` (the
  kit's `scripts/parity/`, the theme's `tests/parity/`; `make <route>` per page, `list`, `remove`: noindex copies at
  `/kit-long-test-<page>/`, removed by their stored IDs), not `design-check.mjs --long`, which only checks them.
  `qa-long-content` with `[QA-LONG]` stays for an older kit; Next.js keeps its `/qa-long-content` route. SKILL.md's
  live check says "the long content test pages removed".

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
