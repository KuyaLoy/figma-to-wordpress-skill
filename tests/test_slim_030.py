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

# 0.2.15 SKILL.md lines changed on purpose later (the old line, and the release that changed it).
CHANGED = {
    '**All rules at the plan:** every form and where its leads go (the leads portal, or "none: <reason>"), missing':
        '0.3.2: the leads portal is optional',
    'content (marked placeholders), the live plugin checklist (WordPress), tracking, redirects, a chat or search.':
        '0.3.2: the same item, rewrapped',
    "| 3 Forms and email | Contact Form 7 forms with the branded emails, spam protection, thank-you page; form "
    "attribution and the leads portal sender (`references/wordpress.md`) | Server actions or a route handler with "
    "validation, spam protection, the task's mail service, form attribution and the leads portal sender "
    "(`references/nextjs.md`) |": '0.3.2: the leads portal sender only when the profile names one',
    'the leads portal on every lead form, live QA, and the report (`_figma/report.md`, DONE first). The developer types':
        '0.3.2: the leads portal is optional',
    'every live password, licence key and API key.': '0.3.2: the same sentence, rewrapped',
    'route built from typed content (Next.js); forms, emails, form attribution and the leads portal proven on live; the':
        '0.3.2: the leads portal is optional',
    '4. **Check your own work:** `node <kit>/scripts/check.mjs --base <url> --route <path> --page <page> --section':
        '0.4.0: the self-check framing removed, the check kept (STEPS_040)',
    '2. One fresh read-only check (a subagent; in Claude Code on a cheaper model such as Sonnet; other tools: > '
    'In other':
        '0.4.0: a reader that never saw the build (STEPS_040)',
    "tools; without subagents, a new chat told to only read): the check's numbers first, images only for its failures,":
        '0.4.0: the same item, rewrapped',
    "4. Publish the progress page (the run's findings with their status), report the phase's stop (rule 11) and go":
        "0.4.0: the stop report carries the phase's Pass|Fail lines (STEPS_040)",
    'straight on to the next phase. No go is needed between phases.': '0.4.0: the same item, rewrapped',
}
# The phase table as 0.3.2 words it (the only change since 0.2.15).
PHASES_032 = [
    ('form attribution and the leads portal sender (`references/wordpress.md`)',
     'form attribution, and the leads portal sender only when the profile names one (`references/wordpress.md`)'),
    ('form attribution and the leads portal sender (`references/nextjs.md`)',
     'form attribution, and the leads portal sender only when the profile names one (`references/nextjs.md`)'),
]

# The moved steps as 0.4.0 words them (the token diet: no self-check framing, a reader that never saw the build,
# the phase's Pass|Fail lines in the stop report). Compared with whitespace collapsed.
STEPS_040 = [
    ('4. **Check your own work:** `node', '4. **Check:** `node'),
    ('2. One fresh read-only check (a subagent; in Claude Code on a cheaper model such as Sonnet; other tools: > In '
     'other tools; without subagents, a new chat told to only read):',
     '2. One read-only check by a reader that never saw the build (a subagent run in the background; in Claude Code '
     'on a cheaper model such as Sonnet; other tools: > In other tools; without subagents, a new chat with the same '
     'brief; the chat that built it never stands in):'),
    ("report the phase's stop (rule 11) and go", "report the phase's stop (rule 11) with the phase's `Pass|Fail` "
     'lines (> What each phase must prove) and go'),
]


def flat(text):
    return ' '.join(text.split())


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
            if t and t not in CHANGED:
                self.assertIn(t, have, f'lost from 0.2.15 SKILL.md: {t}')
        for h in re.findall(r'(?m)^#{1,3} .+$', old):
            self.assertIn(h, self.skill, f'heading lost from SKILL.md: {h}')

    def test_rules_unchanged(self):
        rules = section(self.skill, 'Rules (always)')
        self.assertEqual(re.findall(r'(?m)^(\d+)\. \*\*', rules), [str(n) for n in range(1, 14)])
        old = old_skill()
        if old:
            self.assertEqual(rules, section(old, 'Rules (always)'))  # the hard rules word for word
            phases = section(old, 'The phases')
            for a, b in PHASES_032:
                phases = phases.replace(a, b)
            self.assertEqual(section(self.skill, 'The phases'), phases)

    def test_moved_steps_word_for_word(self):
        old = old_skill()
        if old is None:
            self.skipTest('no git or no 0.2.15 tag here')
        for heading, level in (('The section loop (phase 2)', '###'),
                               ('QA (after each phase, and the loop at the end)', '##')):
            want = flat(section(old, heading, level))
            for x, y in STEPS_040:
                want = want.replace(x, y)
            self.assertEqual(flat(section(self.steps, heading)), want, heading)

    def test_pointers_resolve(self):
        heads = re.findall(r'(?m)^## (.+)$', self.steps)
        listed = re.findall(r'(?m)^- (.+)$', section(self.steps, 'Contents'))
        self.assertEqual(listed, [h for h in heads if h != 'Contents'])
        parts = flat(self.skill).split('`references/phase-steps.md` > ')[1:]
        targets = [p.split('`references/')[0] for p in parts]
        self.assertEqual(len(targets), 3)  # section loop, QA, what each phase must prove (0.4.0)
        for t in targets:
            self.assertTrue(any(t.startswith(h) for h in heads), f'pointer to a missing section: {t[:60]}')
        self.assertIn('| `references/phase-steps.md` |', self.skill)


if __name__ == '__main__':
    unittest.main()
