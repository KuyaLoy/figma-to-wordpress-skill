# The progress page

One page shows the developer (and a lead or Command Center) what is done and what is not: phases, every page with
its sections and their status, open QA findings, and a short log. It is rendered from `_figma/progress.json`, the
single source of truth, which is also what a resumed chat reads.

## Commands (`scripts/progress.py`, dir = `<project>/_figma`)

```
progress.py <dir> init --site "Example" --target wordpress --figma <figma url>
progress.py <dir> page home --name "Home" --route / --sections header,hero,faq,footer --desktop 1:2 --mobile 3:4
progress.py <dir> set home hero building          # todo | building | built | checked | fixed
progress.py <dir> set '*' '*' checked             # after a clean full QA; keeps unbuilt and open-finding sections
progress.py <dir> phase pages doing               # plan | setup | pages | forms | seo | fix | qa | golive | live
progress.py <dir> finding add --severity major --page home --section hero --what "..." --expected 32 --measured 24
progress.py <dir> finding fix F-001 --how "gap 32, re-checked 1440 and 375"
progress.py <dir> finding decide F-002 --why "Figma frames disagree: 760 vs 776"
progress.py <dir> log "Header and footer built."
progress.py <dir> url https://claude.ai/artifact/...
progress.py <dir> status                          # summary for a resume
```

Every change re-renders `_figma/progress.html` and prints one line. One write per section (`set ... built`), one
per finding, one per phase change: never more.

## Statuses

| Status | Means |
|---|---|
| `todo` | Not started |
| `building` | Being built now |
| `built` | Built and within the done standard by its own check |
| `checked` | QA passed on it (set after a clean full QA) |
| `fixed` | It had findings; all are fixed and re-checked (set by `finding fix` on its last open finding) |

A section with an open finding gets a red outline and "(n open)" on the page.

## Publishing

- **Claude desktop app (Artifact tool):** publish `_figma/progress.html` once as a private artifact, then save its
  link with `progress.py <dir> url <link>`. After each section and each phase: re-render (automatic) and publish
  the same file again with that link as `url`, so the link stays the same. A new chat reads the link from
  `progress.py <dir> status`.
- **No Artifact tool:** open `_figma/progress.html` in a browser; it is self-contained (no scripts, no requests).
- The page is private: it lists pages, findings and the log, never passwords or keys.

## progress.json shape

```json
{
 "site": "Example", "target": "wordpress", "figma": "https://www.figma.com/design/...", "url": "", "updated": "...",
 "phases": [{"id": "plan", "name": "Plan", "status": "doing"}],
 "pages": [{"slug": "home", "name": "Home", "route": "/", "desktop": "1:2", "mobile": "3:4",
            "sections": [{"slug": "hero", "status": "todo"}]}],
 "findings": [{"id": "F-001", "severity": "major", "page": "home", "section": "hero", "what": "...",
               "expected": "...", "measured": "...", "phase": "pages", "status": "open", "note": "",
               "added": "...", "closed": ""}],
 "log": [{"at": "...", "text": "Started."}]
}
```

Other skills may render the same shape (for example a conversion skill's board): keep these keys stable.
