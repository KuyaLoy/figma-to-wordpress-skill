#!/usr/bin/env python3
"""The self-check of references/qa.md section 7 (it points here), in Python, so it runs in any shell (PowerShell,
cmd, Git Bash, a Mac or Linux terminal). Four searches: one-off values (`text-[19px]`, `bg-[#...]`) in .php, .js,
.jsx and .tsx; raw hex in .css outside the tokens file; Figma node IDs and ticket tags in code; PHPCS ignore
comments in .php. Skips node_modules, vendor, dist, build, .next and .git. The same patterns as the four grep lines
qa.md had before 0.4.0 (tests/test_oneoff.py still runs them against this script).

    python3 oneoff.py [dir]     the theme (WordPress) or the app (Next.js); default: the current folder

Prints every hit as file:line:[label] text, then one OK line with the count. Each hit is fixed or kept with a
one-line reason in the report. The node-ID pattern also matches times and ratios: read the hits, fix only node
IDs. A WordPress theme can use convert-to-wordpress's `scripts/report/text-check.py oneoff <theme>` instead (the
same searches for .php, .js and .css); this one also reads .jsx and .tsx and skips `.next`.

Exit 0 (hits are read, not failed), 2 usage.
"""
import os
import re
import sys

SKIP_DIRS = {'node_modules', 'vendor', 'dist', 'build', '.next', '.git'}
CODE = ('.php', '.js', '.jsx', '.tsx')
SEARCHES = [  # (label, extensions, pattern, drop lines containing)
    ('one-off value', CODE, re.compile(r'[a-z]-\[(#|[0-9])'), None),
    ('raw hex', ('.css',), re.compile(r'#[0-9a-fA-F]{3,8}\b'), 'tokens'),
    ('node ID or ticket tag', CODE, re.compile(r'[0-9]+:[0-9]+|\b[A-Z][A-Z0-9]+-T[0-9]+\b'), None),
    ('phpcs ignore', ('.php',), re.compile(r'phpcs:ignore|phpcs:disable'), None),
]


def walk(root, exts):
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for f in sorted(files):
            if f.endswith(exts):
                yield os.path.join(d, f)


def scan(root):
    """Every hit as (relative path with /, line number, label, stripped text)."""
    hits = []
    for label, exts, pat, drop in SEARCHES:
        for f in walk(root, exts):
            with open(f, encoding='utf-8', errors='replace') as fh:
                for n, line in enumerate(fh, 1):
                    if pat.search(line) and not (drop and drop in line):
                        hits.append((os.path.relpath(f, root).replace(os.sep, '/'), n, label, line.strip()))
    return hits


def main(argv):
    if len(argv) > 1 or (argv and argv[0] in ('-h', '--help')):
        print(__doc__)
        return 2
    root = argv[0] if argv else '.'
    if not os.path.isdir(root):
        print(f'FAIL oneoff: no folder {root}')
        return 2
    hits = scan(root)
    for rel, n, label, text in hits:
        print(f'{rel}:{n}:[{label}] {text}')
    print(f'OK oneoff: {len(hits)} hits; each one fixed or given a one-line reason')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
