"""0.3.0: a slimmer SKILL.md. The section loop's steps and the QA steps moved unchanged to references/phase-steps.md;
SKILL.md keeps the rules word for word, the phase table and a short summary with an "open when" pointer. Nothing is
lost: every heading and every line of the 0.2.15 SKILL.md is still in SKILL.md or a reference."""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SKILL_DIR = os.path.join(ROOT, 'skills', 'figma-to-wordpress')
OLD_TAG = 'figma-to-wordpress--v0.2.15'


def read(*parts):
    with open(os.path.join(SKILL_DIR, *parts), encoding='utf-8') as fh:
        return fh.read()


def section(text, heading, level='##'):
    m = re.search(rf'(?ms)^{level} {re.escape(heading)}\n(.*?)(?=^##+ |\Z)', text)
    return m.group(1) if m else None


def old_skill():
    if not shutil.which('git'):
        return None
    r = subprocess.run(['git', 'show', f'{OLD_TAG}:skills/figma-to-wordpress/SKILL.md'], cwd=ROOT,
                       capture_output=True, text=True, encoding='utf-8')
    return r.stdout if r.returncode == 0 else None


class Slim(unittest.TestCase):
    skill = read('SKILL.md')
    steps = read('references', 'phase-steps.md')

    def test_size(self):
        self.assertLessEqual(len(self.skill), 20000, 'SKILL.md over about 5,000 tokens (4 characters a token)')
        self.assertLess(len(self.skill.splitlines()), 250)

    @unittest.skipIf(old_skill() is None, 'no git or no 0.2.15 tag here')
    def test_nothing_lost(self):
        refs = [read('references', x) for x in sorted(os.listdir(os.path.join(SKILL_DIR, 'references')))
                if x.endswith('.md')]
        have = {line.strip() for text in [self.skill] + refs for line in text.splitlines()}
        old = old_skill()
        for line in old.splitlines():
            t = line.strip()
            if t:
                self.assertIn(t, have, f'lost from 0.2.15 SKILL.md: {t}')
        for h in re.findall(r'(?m)^#{1,3} .+$', old):
            self.assertIn(h, self.skill, f'heading lost from SKILL.md: {h}')

    def test_rules_unchanged(self):
        rules = section(self.skill, 'Rules (always)')
        self.assertEqual(re.findall(r'(?m)^(\d+)\. \*\*', rules), [str(n) for n in range(1, 14)])
        old = old_skill()
        if old:
            self.assertEqual(rules, section(old, 'Rules (always)'))  # the hard rules word for word
            self.assertEqual(section(self.skill, 'The phases'), section(old, 'The phases'))

    def test_moved_steps_word_for_word(self):
        old = old_skill()
        if old is None:
            self.skipTest('no git or no 0.2.15 tag here')
        self.assertEqual(section(self.steps, 'The section loop (phase 2)').strip(),
                         section(old, 'The section loop (phase 2)', '###').strip())
        self.assertEqual(section(self.steps, 'QA (after each phase, and the loop at the end)').strip(),
                         section(old, 'QA (after each phase, and the loop at the end)').strip())

    def test_pointers_resolve(self):
        heads = re.findall(r'(?m)^## (.+)$', self.steps)
        listed = re.findall(r'(?m)^- (.+)$', section(self.steps, 'Contents'))
        self.assertEqual(listed, [h for h in heads if h != 'Contents'])
        for target in re.findall(r'`references/phase-steps\.md` > (.+?\))', self.skill):
            self.assertIn(target, heads, f'pointer to a missing section: {target}')
        self.assertEqual(len(re.findall(r'`references/phase-steps\.md` > ', self.skill)), 2)
        self.assertIn('| `references/phase-steps.md` |', self.skill)


if __name__ == '__main__':
    unittest.main()
