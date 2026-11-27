import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'skills', 'figma-to-wordpress', 'scripts'))
import oneoff  # noqa: E402

FILES = {
    'components/Hero.tsx': 'export const Hero = () => <h1 className="text-[19px] bg-[#fff]">Hi</h1>;\n'
                           '// node 12:345 from ABC1-T8\nconst ok = "text-lg";\n',
    'components/Card.jsx': 'const c = "mt-[3px]";\n',
    'template-parts/hero.php': '<?php // phpcs:ignore WordPress.Security\n$x = 1;\n',
    'assets/site.css': '.a { color: #1c1c1a; }\n.b { color: var(--ink); }\n',
    'assets/tokens.css': ':root { --ink: #1c1c1a; } /* tokens */\n',
    'node_modules/x/y.js': 'const z = "w-[1px]";\n',
    '.next/static/chunk.js': 'const z = "w-[1px]";\n',
    'vendor/a.php': '// phpcs:disable\n',
    'notes.md': 'text-[19px] in a doc is not code\n',
}
EXPECTED = {
    ('components/Hero.tsx', 1, 'one-off value'),
    ('components/Card.jsx', 1, 'one-off value'),
    ('assets/site.css', 1, 'raw hex'),
    ('components/Hero.tsx', 2, 'node ID or ticket tag'),
    ('template-parts/hero.php', 1, 'phpcs ignore'),
}
GREP = [  # the grep lines references/qa.md section 7 had before 0.4.0, still pinned: (options, patterns)
    (['-rnE', '--include=*.php', '--include=*.js', '--include=*.jsx', '--include=*.tsx'], [r'[a-z]-\[(#|[0-9])']),
    (['-rnE', '--include=*.css'], [r'#[0-9a-fA-F]{3,8}\b']),
    (['-rnE', '--include=*.php', '--include=*.js', '--include=*.jsx', '--include=*.tsx'],
     [r'[0-9]+:[0-9]+|\b[A-Z][A-Z0-9]+-T[0-9]+\b']),
    (['-rn', '--include=*.php'], ['phpcs:ignore', 'phpcs:disable']),
]
EXCLUDE = ['--exclude-dir=node_modules', '--exclude-dir=vendor', '--exclude-dir=dist', '--exclude-dir=build',
           '--exclude-dir=.next']


class OneoffTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        for rel, text in FILES.items():
            p = os.path.join(self.root, *rel.split('/'))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'w', encoding='utf-8', newline='\n') as f:
                f.write(text)

    def tearDown(self):
        self.tmp.cleanup()

    def test_hits_skips_and_tokens(self):
        got = {(rel, n, label) for rel, n, label, _ in oneoff.scan(self.root)}
        self.assertEqual(got, EXPECTED)

    def test_output_and_exit(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = oneoff.main([self.root])
        self.assertEqual(code, 0)
        out = buf.getvalue().splitlines()
        self.assertIn('components/Card.jsx:1:[one-off value] const c = "mt-[3px]";', out)
        self.assertEqual(out[-1], 'OK oneoff: 5 hits; each one fixed or given a one-line reason')
        with redirect_stdout(io.StringIO()):
            self.assertEqual(oneoff.main([os.path.join(self.root, 'missing')]), 2)

    @unittest.skipUnless(shutil.which('grep'), 'grep not installed')
    def test_same_hits_as_the_grep_lines(self):
        got = set()
        for i, (opts, patterns) in enumerate(GREP):
            pf = os.path.join(self.root, '..', f'pattern{i}.txt')  # -f: Windows grep mangles regex arguments
            with open(pf, 'w', encoding='utf-8', newline='\n') as f:
                f.write('\n'.join(patterns) + '\n')
            out = subprocess.run(['grep'] + opts + EXCLUDE + ['-f', os.path.abspath(pf), '.'], cwd=self.root,
                                 capture_output=True, text=True).stdout
            os.remove(pf)
            for line in out.splitlines():
                rel, n, text = line.split(':', 2)
                if i == 1 and 'tokens' in text:  # the "| grep -v tokens" of the raw hex line
                    continue
                got.add((rel[2:] if rel.startswith('./') else rel, int(n), oneoff.SEARCHES[i][0]))
        self.assertEqual(got, EXPECTED)


if __name__ == '__main__':
    unittest.main()
