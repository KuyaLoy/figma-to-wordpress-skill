#!/usr/bin/env python3
"""Progress of a Figma build: pages x sections x status, phases, QA findings and a short log.

The state lives in <dir>/progress.json (usually <project>/_figma). Every change re-renders <dir>/progress.html, a
self-contained page that is published as a private artifact (or opened locally). Prints one short line per call.

  progress.py <dir> init --site "Example" --target wordpress [--figma URL] [--force]
  progress.py <dir> page <slug> --name "Home" --route / --sections hero,services,faq [--desktop 1:2] [--mobile 3:4]
  progress.py <dir> set <page|*> <section|*> <todo|building|built|checked|fixed>
  progress.py <dir> phase <plan|setup|pages|forms|seo|fix|qa|golive|live> <todo|doing|done>
  progress.py <dir> finding add --severity major --page home --section hero --what "..." [--expected ..] [--measured ..]
  progress.py <dir> finding fix <F-001> --how "re-checked at 1440 and 375"
  progress.py <dir> finding decide <F-001> --why "Figma itself is inconsistent: ..."
  progress.py <dir> log "text"
  progress.py <dir> url <artifact url>
  progress.py <dir> status            (summary: phases, counts, open findings, next section)
  progress.py <dir> render            (only re-render the page)
"""
import argparse
import html
import json
import os
import sys
from datetime import datetime

STATUSES = ['todo', 'building', 'built', 'checked', 'fixed']
PHASES = [
    ('plan', 'Plan'), ('setup', '1 Setup'), ('pages', '2 Pages'), ('forms', '3 Forms and email'),
    ('seo', '4 SEO, security, speed'), ('fix', 'Fix list'), ('qa', 'QA until 0'), ('golive', 'Go-live gate'),
    ('live', 'Live and report'),
]
PHASE_STATUSES = ['todo', 'doing', 'done']
SEVERITIES = ['blocker', 'major', 'minor']


def now():
    return datetime.now().astimezone().isoformat(timespec='minutes')


def fail(msg):
    print('ERROR: ' + msg)
    sys.exit(1)


def path(d, name):
    return os.path.join(d, name)


def load(d):
    p = path(d, 'progress.json')
    if not os.path.exists(p):
        fail(f'no progress.json in {d}: run "init" first')
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def save(d, data, line):
    data['updated'] = now()
    tmp = path(d, 'progress.json.tmp')
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write('\n')
    os.replace(tmp, path(d, 'progress.json'))
    render(d, data)
    print(line)


def find_page(data, slug):
    for p in data['pages']:
        if p['slug'] == slug:
            return p
    fail(f'no page "{slug}" (pages: {", ".join(p["slug"] for p in data["pages"]) or "none"})')


def open_findings(data, page=None, section=None):
    return [f for f in data['findings'] if f['status'] == 'open'
            and (page is None or f.get('page') == page) and (section is None or f.get('section') == section)]


def counts(data):
    c = {s: 0 for s in STATUSES}
    for p in data['pages']:
        for s in p['sections']:
            c[s['status']] += 1
    return c


def next_section(data):
    for want in ('building', 'todo'):
        for p in data['pages']:
            for s in p['sections']:
                if s['status'] == want:
                    return f"{p['slug']}/{s['slug']} ({want})"
    return 'none'


# ---------- commands ----------

def cmd_init(a):
    os.makedirs(a.dir, exist_ok=True)
    if os.path.exists(path(a.dir, 'progress.json')) and not a.force:
        fail('progress.json exists; use --force to start over')
    data = {
        'site': a.site, 'target': a.target, 'figma': a.figma or '', 'url': '', 'updated': '',
        'phases': [{'id': i, 'name': n, 'status': 'todo'} for i, n in PHASES],
        'pages': [], 'findings': [], 'log': [{'at': now(), 'text': 'Started.'}],
    }
    data['phases'][0]['status'] = 'doing'
    save(a.dir, data, f'OK init {a.site} ({a.target})')


def cmd_page(a):
    data = load(a.dir)
    sections = [s.strip() for s in (a.sections or '').split(',') if s.strip()]
    if not sections:
        fail('--sections needs at least one section slug')
    if len(set(sections)) != len(sections):
        fail('a section slug is listed twice')
    entry = {'slug': a.slug, 'name': a.name or a.slug, 'route': a.route or '', 'desktop': a.desktop or '',
             'mobile': a.mobile or '', 'sections': [{'slug': s, 'status': 'todo'} for s in sections]}
    old = next((p for p in data['pages'] if p['slug'] == a.slug), None)
    if old:
        keep = {s['slug']: s['status'] for s in old['sections']}
        for s in entry['sections']:
            s['status'] = keep.get(s['slug'], 'todo')
        data['pages'][data['pages'].index(old)] = entry
        verb = 'updated'
    else:
        data['pages'].append(entry)
        verb = 'added'
    save(a.dir, data, f'OK page {a.slug} {verb} ({len(sections)} sections)')


def cmd_set(a):
    if a.status not in STATUSES:
        fail(f'status must be one of {", ".join(STATUSES)}')
    data = load(a.dir)
    pages = data['pages'] if a.page == '*' else [find_page(data, a.page)]
    changed, skipped = 0, 0
    for p in pages:
        secs = p['sections'] if a.section == '*' else [s for s in p['sections'] if s['slug'] == a.section]
        if not secs and a.section != '*':
            fail(f'no section "{a.section}" on page "{p["slug"]}"')
        for s in secs:
            if a.status == 'checked' and (s['status'] in ('todo', 'building', 'fixed')
                                          or open_findings(data, p['slug'], s['slug'])):
                skipped += 1
                continue
            if s['status'] != a.status:
                s['status'] = a.status
                changed += 1
    extra = f', {skipped} kept (not built, already fixed, or open findings)' if skipped else ''
    save(a.dir, data, f'OK {changed} section(s) -> {a.status}{extra}. Next: {next_section(data)}')


def cmd_phase(a):
    if a.status not in PHASE_STATUSES:
        fail(f'phase status must be one of {", ".join(PHASE_STATUSES)}')
    data = load(a.dir)
    ph = next((p for p in data['phases'] if p['id'] == a.phase), None)
    if not ph:
        fail(f'no phase "{a.phase}" ({", ".join(i for i, _ in PHASES)})')
    ph['status'] = a.status
    data['log'].append({'at': now(), 'text': f'Phase {ph["name"]}: {a.status}.'})
    save(a.dir, data, f'OK phase {a.phase} -> {a.status}')


def cmd_finding(a):
    data = load(a.dir)
    if a.action == 'add':
        if a.severity not in SEVERITIES:
            fail(f'--severity must be one of {", ".join(SEVERITIES)}')
        if not a.what:
            fail('--what is required')
        if a.page:
            page = find_page(data, a.page)
            if a.section and a.section not in [s['slug'] for s in page['sections']]:
                fail(f'no section "{a.section}" on page "{a.page}"')
        for f in open_findings(data, a.page, a.section):
            if f['what'].strip().lower() == a.what.strip().lower():
                print(f'OK duplicate of {f["id"]}, not added')
                return
        fid = f'F-{len(data["findings"]) + 1:03d}'
        data['findings'].append({
            'id': fid, 'severity': a.severity, 'page': a.page or '', 'section': a.section or '', 'what': a.what,
            'expected': a.expected or '', 'measured': a.measured or '', 'phase': a.phase or current_phase(data),
            'status': 'open', 'note': '', 'added': now(), 'closed': '',
        })
        save(a.dir, data, f'OK {fid} added ({a.severity}). Open: {len(open_findings(data))}')
        return
    if not a.id:
        fail('finding id required')
    f = next((x for x in data['findings'] if x['id'] == a.id), None)
    if not f:
        fail(f'no finding {a.id}')
    note = a.how if a.action == 'fix' else a.why
    if not note:
        fail('--how is required to fix' if a.action == 'fix' else '--why is required to decide')
    f['status'] = 'fixed' if a.action == 'fix' else 'decided'
    f['note'], f['closed'] = note, now()
    if f['page'] and f['section'] and not open_findings(data, f['page'], f['section']):
        for p in data['pages']:
            for s in p['sections']:
                if p['slug'] == f['page'] and s['slug'] == f['section'] and s['status'] in ('built', 'checked'):
                    s['status'] = 'fixed'
    save(a.dir, data, f'OK {a.id} {f["status"]}. Open: {len(open_findings(data))}')


def current_phase(data):
    doing = [p['id'] for p in data['phases'] if p['status'] == 'doing']
    return doing[-1] if doing else ''


def cmd_log(a):
    data = load(a.dir)
    data['log'].append({'at': now(), 'text': a.text})
    save(a.dir, data, 'OK logged')


def cmd_url(a):
    data = load(a.dir)
    data['url'] = a.url
    save(a.dir, data, f'OK page url saved: {a.url}')


def cmd_status(a):
    data = load(a.dir)
    c = counts(data)
    total = sum(c.values())
    phases = ' | '.join(f"{p['id']}:{p['status']}" for p in data['phases'])
    of = open_findings(data)
    sev = {s: sum(1 for f in of if f['severity'] == s) for s in SEVERITIES}
    print(f"{data['site']} ({data['target']}) updated {data['updated']}")
    print(f'Phases: {phases}')
    print(f'Sections: {total} | ' + ' '.join(f'{k} {v}' for k, v in c.items()))
    print(f"Open findings: {len(of)} (blocker {sev['blocker']}, major {sev['major']}, minor {sev['minor']})")
    print(f'Next section: {next_section(data)}')
    print(f"Page: {data['url'] or 'not published yet'}")
    if data['log']:
        print(f"Last log: {data['log'][-1]['at']} {data['log'][-1]['text']}")


def cmd_render(a):
    data = load(a.dir)
    render(a.dir, data)
    print(f'OK rendered {path(a.dir, "progress.html")}')


# ---------- the page ----------

CSS = """
:root{--bg:#f7f7f5;--card:#fff;--ink:#1c1c1a;--mute:#6b6b66;--line:#e4e3de;--todo:#d9d8d2;--building:#f2b84b;
--built:#5b8def;--checked:#3fa66b;--fixed:#2d8a8a;--open:#d9534f;--chipink:#fff}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#151514;--card:#1f1f1d;--ink:#ecebe6;
--mute:#a3a29b;--line:#34332f;--todo:#4a4944;--building:#c9962f;--built:#4a76c9;--checked:#2f8a56;--fixed:#2a7a7a;
--open:#c9473f}}
:root[data-theme="dark"]{--bg:#151514;--card:#1f1f1d;--ink:#ecebe6;--mute:#a3a29b;--line:#34332f;--todo:#4a4944;
--building:#c9962f;--built:#4a76c9;--checked:#2f8a56;--fixed:#2a7a7a;--open:#c9473f}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px 48px}h1{font-size:26px;margin:0 0 4px}
h2{font-size:18px;margin:28px 0 10px}.mute{color:var(--mute)}.card{background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:14px 16px}.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));
gap:10px;margin-top:16px}.stat b{display:block;font-size:24px}.phases{display:flex;flex-wrap:wrap;gap:6px}
.ph{padding:5px 10px;border-radius:999px;border:1px solid var(--line);font-size:13px}.ph-doing{border-color:
var(--building);font-weight:600}.ph-done{background:var(--checked);border-color:var(--checked);color:var(--chipink)}
.bar{display:flex;height:10px;border-radius:999px;overflow:hidden;background:var(--todo);margin-top:12px}
table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:8px 6px;border-top:1px solid var(--line);
vertical-align:top}th{font-size:13px;color:var(--mute);font-weight:500}.chips{display:flex;flex-wrap:wrap;gap:4px}
.chip{font-size:12px;padding:2px 8px;border-radius:999px;color:var(--chipink);white-space:nowrap}
.todo{background:var(--todo);color:var(--ink)}.building{background:var(--building);color:#1c1c1a}
.built{background:var(--built)}.checked{background:var(--checked)}.fixed{background:var(--fixed)}
.chip.has-open{outline:2px solid var(--open);outline-offset:1px}.sev{font-weight:600}.sev.blocker,.sev.major{
color:var(--open)}.legend{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}.scroll{overflow-x:auto}
ul.log{list-style:none;padding:0;margin:0}ul.log li{padding:4px 0;border-top:1px solid var(--line)}
@media (max-width:640px){td,th{padding:6px 4px}.hide-sm{display:none}}
"""


def e(s):
    return html.escape(str(s or ''))


def render(d, data):
    c = counts(data)
    total = sum(c.values()) or 1
    of = open_findings(data)
    done = c['checked'] + c['fixed']
    bar = ''.join(f'<span class="{s}" style="width:{c[s] * 100 / total:.2f}%"></span>'
                  for s in ('fixed', 'checked', 'built', 'building'))
    phases = ''.join(f'<span class="ph ph-{p["status"]}">{e(p["name"])}</span>' for p in data['phases'])
    legend = ''.join(f'<span class="chip {s}">{s}</span>' for s in STATUSES)
    rows = []
    for p in data['pages']:
        chips = []
        for s in p['sections']:
            n = len(open_findings(data, p['slug'], s['slug']))
            mark = f' ({n} open)' if n else ''
            chips.append(f'<span class="chip {s["status"]}{" has-open" if n else ""}" '
                         f'title="{e(s["slug"])}: {s["status"]}{mark}">{e(s["slug"])}{mark}</span>')
        pdone = sum(1 for s in p['sections'] if s['status'] in ('checked', 'fixed'))
        rows.append(f'<tr><td><b>{e(p["name"])}</b><br><span class="mute">{e(p["route"])}</span></td>'
                    f'<td><div class="chips">{"".join(chips)}</div></td>'
                    f'<td class="hide-sm">{pdone}/{len(p["sections"])}</td></tr>')
    frows = ''.join(
        f'<tr><td>{e(f["id"])}</td><td class="sev {e(f["severity"])}">{e(f["severity"])}</td>'
        f'<td>{e(f["page"])}{"/" + e(f["section"]) if f["section"] else ""}</td><td>{e(f["what"])}'
        f'{"<br><span class=mute>Figma: " + e(f["expected"]) + "</span>" if f["expected"] else ""}'
        f'{"<br><span class=mute>Measured: " + e(f["measured"]) + "</span>" if f["measured"] else ""}</td></tr>'
        for f in of)
    closed = [f for f in data['findings'] if f['status'] != 'open']
    log = ''.join(f'<li><span class="mute">{e(x["at"][:16].replace("T", " "))}</span> {e(x["text"])}</li>'
                  for x in reversed(data['log'][-25:]))
    title = f'{data["site"]} build progress'
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><style>{CSS}</style></head><body><main>
<h1>{e(title)}</h1>
<div class="mute">Target: {e(data["target"])} &middot; Updated {e(data["updated"][:16].replace("T", " "))}</div>
<div class="stats">
<div class="card stat"><b>{done}/{sum(c.values())}</b>sections done</div>
<div class="card stat"><b>{c["building"] + c["built"]}</b>building or built</div>
<div class="card stat"><b>{c["todo"]}</b>to do</div>
<div class="card stat"><b>{len(of)}</b>open findings</div>
</div>
<div class="bar">{bar}</div>
<h2>Phases</h2><div class="phases">{phases}</div>
<h2>Pages and sections</h2><div class="legend">{legend}</div>
<div class="card scroll"><table><tr><th>Page</th><th>Sections</th><th class="hide-sm">Done</th></tr>
{''.join(rows) or '<tr><td colspan="3" class="mute">No pages yet.</td></tr>'}</table></div>
<h2>Open QA findings ({len(of)})</h2>
<div class="card scroll"><table><tr><th>ID</th><th>Severity</th><th>Where</th><th>What</th></tr>
{frows or '<tr><td colspan="4" class="mute">None open.</td></tr>'}</table>
<p class="mute">{len(closed)} closed (fixed or decided).</p></div>
<h2>Log</h2><div class="card"><ul class="log">{log}</ul></div>
</main></body></html>
"""
    with open(path(d, 'progress.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(page)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('dir')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('init')
    p.add_argument('--site', required=True)
    p.add_argument('--target', choices=['wordpress', 'nextjs'], default='wordpress')
    p.add_argument('--figma')
    p.add_argument('--force', action='store_true')
    p = sub.add_parser('page')
    p.add_argument('slug')
    for opt in ('--name', '--route', '--sections', '--desktop', '--mobile'):
        p.add_argument(opt)
    p = sub.add_parser('set')
    p.add_argument('page')
    p.add_argument('section')
    p.add_argument('status')
    p = sub.add_parser('phase')
    p.add_argument('phase')
    p.add_argument('status')
    p = sub.add_parser('finding')
    p.add_argument('action', choices=['add', 'fix', 'decide'])
    p.add_argument('id', nargs='?')
    for opt in ('--severity', '--page', '--section', '--what', '--expected', '--measured', '--phase', '--how',
                '--why'):
        p.add_argument(opt)
    p = sub.add_parser('log')
    p.add_argument('text')
    p = sub.add_parser('url')
    p.add_argument('url')
    sub.add_parser('status')
    sub.add_parser('render')
    a = ap.parse_args(argv)
    {'init': cmd_init, 'page': cmd_page, 'set': cmd_set, 'phase': cmd_phase, 'finding': cmd_finding,
     'log': cmd_log, 'url': cmd_url, 'status': cmd_status, 'render': cmd_render}[a.cmd](a)


if __name__ == '__main__':
    main()
