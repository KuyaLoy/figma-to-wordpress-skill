"""0.5.0: lean tool output. Long command output goes to a log in _figma/logs/ and the chat gets the command, the
result line, the failures and the log path (SKILL.md > Long output, references/qa.md section 11); compact flags at
the command sites. SKILL.md is not larger than 0.4.1: the In other tools bullets moved word for word to
references/other-tools.md. No rule, heading or check removed."""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SKILL_DIR = os.path.join(ROOT, 'skills', 'figma-to-wordpress')
OLD_TAG = 'figma-to-wordpress--v0.4.1'
SIZE_041 = 18579  # bytes of the 0.4.1 SKILL.md


def read(*parts):
    with open(os.path.join(SKILL_DIR, *parts), encoding='utf-8') as fh:
        return fh.read()


def flat(text):
    return ' '.join(text.split())


def section(text, heading):
    m = re.search(rf'(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)', text)
    return m.group(1) if m else None


def old(path):
    if not shutil.which('git'):
        return None
    r = subprocess.run(['git', 'show', f'{OLD_TAG}:skills/figma-to-wordpress/{path}'], cwd=ROOT,
                       capture_output=True, text=True, encoding='utf-8')
    return r.stdout if r.returncode == 0 else None


REFS = sorted(x for x in os.listdir(os.path.join(SKILL_DIR, 'references')) if x.endswith('.md'))


class LeanOutput(unittest.TestCase):
    skill = read('SKILL.md')
    qa = read('references', 'qa.md')

    def test_skill_not_larger(self):
        self.assertLessEqual(len(self.skill.encode('utf-8')), SIZE_041)

    def test_the_rule(self):
        rule = flat(section(self.skill, 'Long output (always)') or '')
        for s in ('over about 50 lines', '`_figma/logs/<step>.log`', 'the command, its result line, the failures and '
                  'the log path', '`_figma/qa/`', '`references/qa.md` section 11'):
            self.assertIn(s, rule)
        self.assertLess(self.skill.index('## Long output (always)'), self.skill.index('## Start'))

    def test_qa_section_11(self):
        heads = re.findall(r'(?m)^## (.+)$', self.qa)
        self.assertEqual(heads[-1], '11. Long output to a log (every command)')
        s11 = flat(section(self.qa, heads[-1]))
        for s in ('`check.mjs`', '`_figma/logs/<step>.log`', '2>&1', 'Out-File -Encoding utf8', '`_plan/logs/`',
                  '--no-audit --no-fund --loglevel=error', '--reporter=line', '-q --report=summary',
                  '--no-interaction --no-progress', '--porcelain', 'never served and never committed', 'rule 8'):
            self.assertIn(s, s11)
        self.assertIn('11 for any long command', flat(self.qa))

    def test_flags_at_command_sites(self):
        self.assertIn('`npm i -D playwright pixelmatch pngjs --no-audit --no-fund --loglevel=error`', self.qa)
        self.assertIn('`vendor/bin/phpcs -q --report=summary`', section(self.qa, '7. Code gates and the self-check '
                                                                          '(every phase gate, and before DONE)'))
        self.assertIn('`npm run build > _figma/logs/build.log 2>&1`', read('references', 'nextjs.md'))
        self.assertIn('`_figma/logs/build.log`', read('references', 'phase-steps.md'))

    def test_figma_kept_private(self):
        files = flat(section(self.skill, 'Project files (private)'))
        for s in ('Require all denied', 'outside `public/`', 'add `_figma/` to `.gitignore`'):
            self.assertIn(s, files)

    def test_other_tools_moved_word_for_word(self):
        before = old('SKILL.md')
        if before is None:
            self.skipTest('no git or no 0.4.1 tag here')
        bullets = re.findall(r'(?ms)^- \*\*.+?(?=^- \*\*|\n\n)', section(before, 'In other tools (Codex, Antigravity, '
                                                                         'T3 Code and others)'))
        self.assertEqual(len(bullets), 7)
        moved = flat(read('references', 'other-tools.md'))
        for b in bullets:
            self.assertIn(flat(b), moved)
        self.assertIn('`references/other-tools.md`', section(self.skill, 'In other tools (Codex, Antigravity, '
                                                                       'T3 Code and others)'))
        self.assertIn('| `references/other-tools.md` |', self.skill)

    def test_nothing_lost_since_041(self):
        before = old('SKILL.md')
        if before is None:
            self.skipTest('no git or no 0.4.1 tag here')
        have = {line.strip() for text in [self.skill] + [read('references', r) for r in REFS]
                for line in text.splitlines()}
        for line in before.splitlines():
            t = line.strip()
            if t:
                self.assertIn(t, have, f'lost from 0.4.1 SKILL.md: {t}')
        for h in re.findall(r'(?m)^#{1,3} .+$', before):
            self.assertIn(h, self.skill, f'heading lost from SKILL.md: {h}')
        for name in ('Rules (always)', 'The phases', 'Done means'):
            self.assertEqual(section(self.skill, name), section(before, name), name)
        for r in REFS:
            prev = old(f'references/{r}')
            if not prev:
                continue  # new in 0.5.0
            for h in re.findall(r'(?m)^#{1,3} .+$', prev):
                self.assertIn(h, read('references', r), f'heading lost from {r}: {h}')


if __name__ == '__main__':
    unittest.main()
