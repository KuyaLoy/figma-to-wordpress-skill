# The progress page

One page shows the developer (and a lead or Command Center) what is happening and what is done: at the top, in large
type, Now (the step and the time it started), Next, anything waiting or blocked, and the time the page was rendered
("n min ago" while it is open); then phases, every page with its sections and their status, every QA finding with
its status, and a short log. It is rendered from `_figma/progress.json`, the single source of truth, which is also
what a resumed chat reads.

## Commands (`scripts/progress.py`, dir = `<project>/_figma`)

```
progress.py <dir> init --site "Example" --target wordpress --figma <figma url>
progress.py <dir> now "Home: hero" --next "Home: services"   # the Now/Next line; --waiting "..." --blocked "..."
progress.py <dir> page home --name "Home" --route / --sections header,hero,faq,footer --desktop 1:2 --mobile 3:4
progress.py <dir> set home hero building          # todo | building | built | checked | fixed
progress.py <dir> set '*' '*' checked             # after a clean full QA; keeps unbuilt and open-finding sections
progress.py <dir> phase pages doing               # plan | setup | pages | forms | seo | fix | qa | golive | live
progress.py <dir> finding add --severity major --page home --section hero --what "..." --expected 32 --measured 24
progress.py <dir> finding add ... --phase "qa run 2"   # in the QA-until-0 loop: name the run (default: the phase)
progress.py <dir> finding fix F-001 --how "gap 32, re-checked 1440 and 375"
progress.py <dir> finding decide F-002 --why "Figma frames disagree: 760 vs 776"
progress.py <dir> log "Header and footer built."
progress.py <dir> url https://claude.ai/artifact/... [--live]   # --live: the live page's link
progress.py <dir> status                          # summary for a resume
progress.py <dir> render                          # re-render only (the update time becomes now)
progress.py <dir> render --pushed                 # after the rows in progress-rows.json went to the database
```

Every change re-renders `_figma/progress.html` and prints one line. One write per section (`set ... built`), one
per finding, one per phase change, one `now` per step: never more.

`now` replaces the whole line: Next, Waiting and Blocked are cleared unless given again. The same step again keeps
its start time. Write it when a step starts (a section, a QA run, a fix batch, waiting on the developer).

## Statuses

| Status | Means |
|---|---|
| `todo` | Not started |
| `building` | Being built now |
| `built` | Built and within the done standard by its own check |
| `checked` | QA passed on it (set after a clean full QA) |
| `fixed` | It had findings; all are fixed and re-checked (set by `finding fix` on its last open finding) |

A section with an open finding gets a red outline and "(n open)" on the page.

Findings are `open`, `fixed` (with how it was verified) or `decided` (kept on purpose, with why). The page lists
every finding: counts per status and per QA run (the finding's `phase`), open first by severity, fixed and decided
folded below.

## Publishing

- **When:** `progress.json` and `progress.html` update on every write (per section). The page is **published** at
  every unit end: the plan, each page built (its last section), each QA run collected, each fix batch, QA at 0,
  live; and at every stop (a checkpoint, waiting on the developer, paused, blocked). A page of 8 sections publishes
  once, not 8 times.
- **Before a long step** (a QA run, a full pixel run, a fix batch): write `now` first, publish, then start, so the
  page says what the chat is doing. A phase that runs for hours is many units, not one: a page that still shows
  this morning's open findings is wrong.
- **Claude (Artifact tool): the live page,** below. It updates itself; "publish" means push the rows.
- **Other tools:** open `_figma/progress.html` in a browser (self-contained: no requests; one tiny inline script
  shows "n min ago"); the developer refreshes it at the same moments. Where Claude has no artifact database,
  publish `_figma/progress.html` once as a private artifact, save its link with `progress.py <dir> url <link>`,
  and republish the same file to that link at the moments above.
- The page is private: it lists pages, findings and the log, never passwords or keys.

## The live page (Claude, where the artifact database is there)

Every render also writes `_figma/progress-live.html` and `_figma/progress-rows.json` (`scripts/live.py`). Publish
the live page once, privately, with
`capabilities: {"db": {"rules": [{"path": "", "read": "view", "write": "admin"}]}}`, and save its link with
`progress.py <dir> url <link> --live` (`"live_url"` in progress.json). From then on the open page updates itself; at
each step start and stop:

1. The `progress.py` write for the step (`now`, `set`, `finding`, `phase`, `log`): it renders and says how many
   database writes are waiting.
2. Send each batch in progress-rows.json with ArtifactData `batch` (url = live_url; at most 50 writes each). A write
   to a document listed in `"existing"` needs its version: one ArtifactData `list` of that collection gives every
   version; add it as `if_version`. A refused batch (someone else wrote, or the versions moved) writes nothing:
   list again, retry once.
3. Then `progress.py <dir> render --pushed`, so the next render sends only what changed.

Most steps send two or three writes (meta/now, a section, a log line). Republish the live page only when the skill's
page changes. Without the database (a local preview, another tool) the page shows the data of its last render.

| Collection / doc | Fields (the same as convert-to-wordpress 0.9.6) |
|---|---|
| `meta/now` | site, target, now, nowStarted, next, waiting, blocked, updated, static (the static page link) |
| `phases/<id>` | id, name, status (todo, doing, done), order |
| `items/<page>--<section>` | group (page name), page (slug), route, name (section slug), status, order |
| `findings/<id>` | ref, text, where (page/section), run (the finding's phase or QA run), severity, status |
| `log/L<hash>` | at, text (only added; the page shows the newest 30) |

progress.json stays the source of truth; the rows are made from it.

## progress.json shape

```json
{
 "site": "Example", "target": "wordpress", "figma": "https://www.figma.com/design/...", "url": "", "live_url": "",
 "updated": "...",
 "now": {"step": "Home: hero", "started": "2026-11-20T14:05+08:00"}, "next": "Home: services", "waiting": "",
 "blocked": "",
 "phases": [{"id": "plan", "name": "Plan", "status": "doing"}],
 "pages": [{"slug": "home", "name": "Home", "route": "/", "desktop": "1:2", "mobile": "3:4",
            "sections": [{"slug": "hero", "status": "todo"}]}],
 "findings": [{"id": "F-001", "severity": "major", "page": "home", "section": "hero", "what": "...",
               "expected": "...", "measured": "...", "phase": "pages", "status": "open", "note": "",
               "added": "...", "closed": ""}],
 "log": [{"at": "...", "text": "Started."}]
}
```

`updated` is the time of the last write or render, ISO with minutes. `now`, `next`, `waiting` and `blocked` came in
0.2.6 (the same keys as convert-to-wordpress 0.9.5's board), `live_url` in 0.2.7; a file without them still loads
and renders. The live page's state lives next to it: `progress-rows.json` (to push) and `progress-pushed.json`
(what the database holds).

Other skills may render the same shape (for example a conversion skill's board): keep these keys stable, only add.
