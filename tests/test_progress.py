import io
import json
import os
import sys
import tempfile
import unittest
import webbrowser
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'skills', 'figma-to-wordpress', 'scripts'))
import progress  # noqa: E402


def run(*argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        try:
            progress.main(list(argv))
        except SystemExit as e:
            if e.code:
                return 'EXIT ' + buf.getvalue()
    return buf.getvalue()


class ProgressTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = os.path.join(self.tmp.name, '_figma')
        run(self.d, 'init', '--site', 'Example <Co>', '--target', 'nextjs')
        run(self.d, 'page', 'home', '--name', 'Home', '--route', '/', '--sections', 'hero,services,faq')

    def tearDown(self):
        self.tmp.cleanup()

    def data(self):
        with open(os.path.join(self.d, 'progress.json'), encoding='utf-8') as f:
            return json.load(f)

    def test_init_refuses_overwrite(self):
        self.assertIn('EXIT', run(self.d, 'init', '--site', 'X'))
        self.assertEqual(self.data()['site'], 'Example <Co>')

    def test_set_and_next(self):
        out = run(self.d, 'set', 'home', 'hero', 'built')
        self.assertIn('Next: home/services (todo)', out)
        self.assertEqual(self.data()['pages'][0]['sections'][0]['status'], 'built')
        self.assertIn('EXIT', run(self.d, 'set', 'home', 'nope', 'built'))
        self.assertIn('EXIT', run(self.d, 'set', 'home', 'hero', 'done'))

    def test_checked_skips_open_findings_and_unbuilt(self):
        run(self.d, 'set', 'home', '*', 'built')
        run(self.d, 'set', 'home', 'faq', 'todo')
        run(self.d, 'finding', 'add', '--severity', 'major', '--page', 'home', '--section', 'hero', '--what', 'Too tall')
        run(self.d, 'set', '*', '*', 'checked')
        st = {s['slug']: s['status'] for s in self.data()['pages'][0]['sections']}
        self.assertEqual(st, {'hero': 'built', 'services': 'checked', 'faq': 'todo'})

    def test_finding_lifecycle(self):
        run(self.d, 'set', 'home', 'hero', 'built')
        out = run(self.d, 'finding', 'add', '--severity', 'minor', '--page', 'home', '--section', 'hero',
                  '--what', 'Gap 24 not 32', '--expected', '32', '--measured', '24')
        self.assertIn('F-001 added', out)
        self.assertIn('duplicate of F-001', run(self.d, 'finding', 'add', '--severity', 'minor', '--page', 'home',
                                                 '--section', 'hero', '--what', 'gap 24 not 32'))
        self.assertIn('EXIT', run(self.d, 'finding', 'fix', 'F-001'))
        self.assertIn('Open: 0', run(self.d, 'finding', 'fix', 'F-001', '--how', 're-checked 1440 and 375'))
        d = self.data()
        self.assertEqual(d['findings'][0]['status'], 'fixed')
        self.assertEqual(d['pages'][0]['sections'][0]['status'], 'fixed')

    def test_page_update_keeps_status(self):
        run(self.d, 'set', 'home', 'hero', 'built')
        run(self.d, 'page', 'home', '--sections', 'hero,cta')
        st = {s['slug']: s['status'] for s in self.data()['pages'][0]['sections']}
        self.assertEqual(st, {'hero': 'built', 'cta': 'todo'})

    def test_render_escapes_and_status(self):
        run(self.d, 'finding', 'add', '--severity', 'blocker', '--what', '<script>x</script>')
        with open(os.path.join(self.d, 'progress.html'), encoding='utf-8') as f:
            page = f.read()
        self.assertNotIn('<script>x', page)
        self.assertIn('&lt;script&gt;', page)
        self.assertIn('Example &lt;Co&gt; build progress', page)
        out = run(self.d, 'status')
        self.assertIn('Open findings: 1 (blocker 1', out)
        self.assertIn('Next section: home/hero (todo)', out)

    def page(self):
        with open(os.path.join(self.d, 'progress.html'), encoding='utf-8') as f:
            return f.read()

    def test_render_refresh_kept_and_open(self):
        """0.2.14: the local page for tools without Artifacts reloads itself and opens once."""
        self.assertNotIn('http-equiv="refresh"', self.page())
        opened = []
        real = webbrowser.open
        webbrowser.open = lambda uri: opened.append(uri) or True
        try:
            out = run(self.d, 'render', '--refresh', '30', '--open')
        finally:
            webbrowser.open = real
        self.assertIn('reloads every 30 s', out)
        self.assertEqual(len(opened), 1)
        self.assertTrue(opened[0].startswith('file:') and opened[0].endswith('progress.html'))
        run(self.d, 'set', 'home', 'hero', 'building')  # a later write keeps the reload
        self.assertIn('<meta http-equiv="refresh" content="30">', self.page())
        self.assertEqual(self.data()['refresh'], 30)
        self.assertIn('EXIT', run(self.d, 'render', '--refresh', '2'))
        run(self.d, 'render', '--refresh', '0')
        self.assertNotIn('http-equiv="refresh"', self.page())
        self.assertNotIn('refresh', self.data())

    def test_now_line_and_every_finding_with_status(self):
        """0.2.6: Now/Next at the top with the start time; open, fixed and decided findings, counted per run."""
        run(self.d, 'set', 'home', '*', 'built')
        for what, phase in (('Gap 24 not 32', 'pages'), ('Icon colour', 'pages'), ('Hover missing', 'qa run 2'),
                            ('Unused rule', 'qa run 2')):
            run(self.d, 'finding', 'add', '--severity', 'major', '--page', 'home', '--section', 'hero',
                '--what', what, '--phase', phase)
        run(self.d, 'finding', 'fix', 'F-001', '--how', 're-checked 1440 and 375')
        run(self.d, 'finding', 'decide', 'F-002', '--why', 'the brand file says so')
        run(self.d, 'finding', 'fix', 'F-004', '--how', 'rule removed')
        out = run(self.d, 'now', 'QA run 2 <full>', '--next', 'fix batch 3', '--waiting', 'nothing')
        self.assertIn('OK now: QA run 2 <full>. Next: fix batch 3', out)
        d = self.data()
        self.assertEqual(d['now']['step'], 'QA run 2 <full>')
        self.assertRegex(d['now']['started'], r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}')
        self.assertEqual((d['next'], d['waiting'], d['blocked']), ('fix batch 3', 'nothing', ''))
        self.assertRegex(d['updated'], r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}')
        started = d['now']['started']
        run(self.d, 'now', 'QA run 2 <full>', '--blocked', 'staging down')  # same step: start time kept
        self.assertEqual(self.data()['now']['started'], started)
        self.assertEqual(self.data()['next'], '')
        html = self.page()
        self.assertLess(html.index('class="card now"'), html.index('<h2>Phases'))
        for part in ('<b>QA run 2 &lt;full&gt;</b>', 'started ' + started[11:16], 'Blocked</span> staging down',
                     'id="ago" data-at=', 'QA findings (4): 1 open', '1 open</span>', '2 fixed</span>',
                     '1 decided</span>', '<td>pages</td><td>2</td><td>0</td><td>1</td><td>1</td>',
                     '<td>qa run 2</td><td>2</td><td>1</td><td>1</td><td>0</td>', 'Fixed and decided (3)',
                     'Decided: the brand file says so', 'Fixed: rule removed'):
            self.assertIn(part, html)
        self.assertLess(html.index('Hover missing'), html.index('Fixed and decided'))
        self.assertIn('Now: QA run 2 <full>', run(self.d, 'status'))

    def test_old_progress_json_still_renders(self):
        """A progress.json made before 0.2.6 (no now, next, waiting, blocked) renders and gains the keys."""
        p = os.path.join(self.d, 'progress.json')
        d = self.data()
        for k in ('now', 'next', 'waiting', 'blocked'):
            del d[k]
        d['updated'] = '2026-11-18T10:26+08:00'
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(d, f)
        self.assertIn('OK rendered', run(self.d, 'render'))
        d = self.data()
        self.assertEqual((d['now'], d['next']), ({'step': '', 'started': ''}, ''))
        self.assertNotEqual(d['updated'], '2026-11-18T10:26+08:00')  # updated = render time
        html = self.page()
        self.assertIn('<b>nothing written</b>', html)
        self.assertIn('QA findings (0): 0 open', html)

    def rows(self):
        with open(os.path.join(self.d, 'progress-rows.json'), encoding='utf-8') as f:
            return json.load(f)

    def test_live_rows_use_the_shared_names(self):
        """0.2.7: the database writes use convert-to-wordpress 0.9.6's collections and fields."""
        run(self.d, 'now', 'Home: hero', '--next', 'Home: services')
        run(self.d, 'finding', 'add', '--severity', 'minor', '--page', 'home', '--section', 'hero', '--what',
            'Gap', '--phase', 'qa run 2')
        r = self.rows()
        w = {f'{x["collection"]}/{x["doc_id"]}': x for b in r['batches'] for x in b}
        self.assertEqual(r['count'], len(w))
        self.assertEqual(r['existing'], [])
        self.assertEqual(sorted(w['meta/now']['data']), ['blocked', 'next', 'now', 'nowStarted', 'site', 'static',
                                                         'target', 'updated', 'waiting'])
        self.assertEqual(w['meta/now']['data']['now'], 'Home: hero')
        self.assertEqual(w['phases/plan']['data'], {'id': 'plan', 'name': 'Plan', 'status': 'doing', 'order': 0})
        self.assertEqual(w['items/home--hero']['data'], {'group': 'Home', 'page': 'home', 'route': '/',
                                                         'name': 'hero', 'status': 'todo', 'order': 0})
        self.assertEqual(w['findings/F-001']['data'], {'ref': 'F-001', 'text': 'Gap', 'where': 'home/hero',
                                                       'run': 'qa run 2', 'severity': 'minor', 'status': 'open'})
        self.assertTrue(any(k.startswith('log/L') for k in w))
        self.assertEqual(r['batches'][-1][-1]['collection'], 'meta')  # meta/now last
        self.assertTrue(all(x['op'] == 'set' for x in w.values()))

    def test_pushed_then_only_changes_with_versions(self):
        run(self.d, 'url', 'https://claude.ai/artifact/LIVE', '--live')
        self.assertIn('marked as pushed', run(self.d, 'render', '--pushed'))
        self.assertEqual(self.rows()['count'], 0)
        out = run(self.d, 'set', 'home', 'hero', 'building')
        self.assertRegex(out, r'\((1|2) database writes to push\)')  # meta/now too when the minute moved
        r = self.rows()
        self.assertEqual(r['url'], 'https://claude.ai/artifact/LIVE')
        self.assertIn('items/home--hero', r['existing'])
        self.assertTrue(set(r['existing']) <= {'items/home--hero', 'meta/now'})
        run(self.d, 'page', 'home', '--sections', 'hero,services')  # faq removed: its item is deleted
        r = self.rows()
        dels = [x['doc_id'] for b in r['batches'] for x in b if x['op'] == 'delete']
        self.assertEqual(dels, ['home--faq'])
        self.assertIn('Live page: https://claude.ai/artifact/LIVE', run(self.d, 'status'))

    def test_batches_hold_at_most_50(self):
        run(self.d, 'page', 'big', '--sections', ','.join(f's{i}' for i in range(70)))
        r = self.rows()
        self.assertGreater(r['count'], 70)
        self.assertTrue(all(len(b) <= 50 for b in r['batches']))
        self.assertEqual(sum(len(b) for b in r['batches']), r['count'])

    def test_live_page_snapshot_and_db(self):
        run(self.d, 'finding', 'add', '--severity', 'major', '--what', '</script><b>x</b>')
        with open(os.path.join(self.d, 'progress-live.html'), encoding='utf-8') as f:
            html = f.read()
        snap = html.split('id="snapshot">', 1)[1].split('</script>', 1)[0]
        self.assertNotIn('</', snap)  # a finding cannot end the data block
        self.assertEqual(json.loads(snap)['findings/F-001']['text'], '</script><b>x</b>')
        for part in ("window.claude.use('db')", "['meta', 'phases', 'items', 'findings', 'log']",
                     'Example &lt;Co> build progress', 'snapshot (no live data in this view)'):
            self.assertIn(part, html)

    def test_phase(self):
        self.assertIn('OK phase setup -> doing', run(self.d, 'phase', 'setup', 'doing'))
        self.assertIn('EXIT', run(self.d, 'phase', 'nope', 'doing'))


if __name__ == '__main__':
    unittest.main()
