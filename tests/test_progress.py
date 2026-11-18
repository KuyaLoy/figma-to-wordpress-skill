import io
import json
import os
import sys
import tempfile
import unittest
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

    def test_phase(self):
        self.assertIn('OK phase setup -> doing', run(self.d, 'phase', 'setup', 'doing'))
        self.assertIn('EXIT', run(self.d, 'phase', 'nope', 'doing'))


if __name__ == '__main__':
    unittest.main()
