"""0.4.0: the token diet. No line tells the agent to check its own work, what each phase must prove is objective
items with the tool that gives the evidence (Pass|Fail), the read-only QA check is a reader that never saw the
build, the self-check's searches are named in the script instead of restated, and SKILL.md has room under its
limit (start steps moved word for word to references/start.md). Nothing is lost since 0.3.2."""
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SKILL_DIR = os.path.join(ROOT, 'skills', 'figma-to-wordpress')
OLD_TAG = 'figma-to-wordpress--v0.3.2'

SELF_CHECK = ('check your own work', 're-read the changed files', 'as if someone else wrote', 'double-check',
              'review your own', 'checked by you afterwards')
SUBJECTIVE = ('raised', 'built in', 'honestly', 'looks right', 'as needed', 'looks good', 'make sure')

# 0.3.2 lines changed on purpose in 0.4.0 (the old line, and why).
CHANGED_040 = {
    '| `references/phase-steps.md` | The section loop and the QA steps, with their commands | Phase 2\'s start; every '
    'phase end |': 'the kit table names start.md and what each phase must prove',
    'build from the spec, check your own work with `check.mjs` until it passes (rule 3), mark it `built`, and publish':
        'self-check framing removed, check.mjs kept',
    '13), one fresh read-only check (a subagent), every finding added once (nothing fixed now, except a blocker), the':
        'a reader that never saw the build',
    "page published, the phase's stop report (rule 11), and straight on: no go is needed between phases. "
    'After phase 4:': 'rewrapped',
    'one full QA run, then fix passes, each re-checking what it changed, until a re-check finds 0; then the go-live':
        'rewrapped',
    'gate. Open `references/phase-steps.md` > QA (after each phase, and the loop at the end) at every phase end (the':
        'rewrapped',
    'steps with their commands).': 'rewrapped',
}
# 0.3.2 reference lines changed on purpose in 0.4.0.
CHANGED_REFS_040 = ('moved unchanged in 0.3.0. Open a section', 'skill folder.', '4. **Check your own work:**',
                    '2. One fresh read-only check', "tools; without subagents, a new chat told to only read)",
                    "4. Publish the progress page (the run's", 'straight on to the next phase.',
                    'A fresh read-only check that changes nothing', '`spawn_agent`; Antigravity',
                    'read. Its brief (fill the brackets):', '- **Self-check** over the theme',
                    'In any shell (PowerShell included)', 'grep lines below;', 'With grep or rg:', '```',
                    'X="--exclude-dir', 'grep -rn', 'In order: one-off values', 'node-ID pattern also matches')


def read(*parts):
    with open(os.path.join(SKILL_DIR, *parts), encoding='utf-8') as fh:
        return fh.read()


def section(text, heading):
    m = re.search(rf'(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)', text)
    return m.group(1) if m else ''


def flat(text):
    return ' '.join(text.split())


def old(path):
    if not shutil.which('git'):
        return None
    r = subprocess.run(['git', 'show', f'{OLD_TAG}:skills/figma-to-wordpress/{path}'], cwd=ROOT,
                       capture_output=True, text=True, encoding='utf-8')
    return r.stdout if r.returncode == 0 else None


REFS = sorted(x for x in os.listdir(os.path.join(SKILL_DIR, 'references')) if x.endswith('.md'))


class TokenDiet(unittest.TestCase):
    skill = read('SKILL.md')
    steps = read('references', 'phase-steps.md')

    def test_room_under_the_limit(self):
        self.assertLess(len(self.skill.encode('utf-8')), 19000)

    def test_no_self_check_lines(self):
        for name, text in [('SKILL.md', self.skill)] + [(r, read('references', r)) for r in REFS]:
            low = text.lower()
            for phrase in SELF_CHECK:
                self.assertNotIn(phrase, low, f'{name}: "{phrase}"')

    def test_must_prove_is_pass_fail_with_evidence(self):
        prove = section(self.steps, 'What each phase must prove')
        self.assertIn('`Pass|Fail | item | evidence`', prove)
        self.assertIn('an item without it is Fail', prove)
        self.assertIn("convert-to-wordpress's SKILL.md > What each phase must prove (0.11.0 or later)", prove)
        bullets = re.findall(r'(?ms)^- \*\*.+?(?=^- \*\*|\Z)', prove)
        evidence = [('(ls)', '`progress.py status`', '(plan.md)', 'notes.md'),
                    ("cwp's P1", '`npm run build`', 'check.mjs el rows', 'debug.log', '(curl -I)'),
                    ('`check.mjs` exit 0', 'state rows', 'long content', 'wp-cli', '(grep)', '(curl -I)'),
                    ("cwp's P3", '(curl)', 'mail capture', 'dataLayer', 'only when the profile names one'),
                    ('check.mjs page rows', '(curl -I)', 'JSON.parse', 'Lighthouse'),
                    ('`--phase "qa run 1"`', '`progress.py status`', '`_figma/report.md`', '**Go-live:**'),
                    ("cwp's P6 Launch and P6 Live QA", '`plugin-check.py --env live`', '`plugin-check.py --done`',
                     '`check.mjs --base <live url>` exit 0', 'PageSpeed Insights', '(its URL)')]
        self.assertEqual(len(bullets), len(evidence))
        for b, ev in zip(bullets, evidence):
            for e in ev:
                self.assertIn(e, b, f'evidence "{e}" missing in {b[:40]}')
            for w in SUBJECTIVE:
                self.assertNotIn(w, b, f'subjective "{w}" in {b[:40]}')
        qa = flat(section(self.skill, 'QA (after each phase, and the loop at the end)'))
        self.assertIn('`references/phase-steps.md` > What each phase must prove as `Pass|Fail | item | evidence`', qa)

    def test_fresh_reader(self):
        qa6 = flat(section(read('references', 'qa.md'), '6. The read-only check (every phase)'))
        for s in ('never saw the build', 'in the background', 'The chat that built it never stands in'):
            self.assertIn(s, qa6)
        for text in (self.steps, self.skill):
            self.assertIn('never saw the build', flat(section(text, 'QA (after each phase, and the loop at the end)')))

    def test_self_check_named_not_restated(self):
        qa7 = section(read('references', 'qa.md'),
                      '7. Code gates and the self-check (every phase gate, and before DONE)')
        self.assertNotIn('grep -rn', qa7)
        self.assertIn("the script's own header", qa7)
        header = read('scripts', 'oneoff.py').split('"""')[1]
        for s in ('one-off values', 'raw hex', 'node IDs and ticket tags', 'PHPCS ignore', 'times and ratios'):
            self.assertIn(s, header)

    def test_start_moved_word_for_word(self):
        before = old('SKILL.md')
        if before is None:
            self.skipTest('no git or no 0.3.2 tag here')
        m = re.search(r'(?ms)^3\. \*\*Intake, once\.\*\*.*?(?=^6\. \*\*Gate)', before)
        self.assertIn(flat(m.group(0)), flat(read('references', 'start.md')))
        self.assertIn('`references/start.md`', self.skill)

    def test_nothing_lost_since_032(self):
        before = old('SKILL.md')
        if before is None:
            self.skipTest('no git or no 0.3.2 tag here')
        have = {line.strip() for text in [self.skill] + [read('references', r) for r in REFS]
                for line in text.splitlines()}
        for line in before.splitlines():
            t = line.strip()
            if t and t not in CHANGED_040:
                self.assertIn(t, have, f'lost from 0.3.2 SKILL.md: {t}')
        for h in re.findall(r'(?m)^#{1,3} .+$', before):
            self.assertIn(h, self.skill, f'heading lost from SKILL.md: {h}')
        self.assertEqual(section(self.skill, 'Rules (always)'), section(before, 'Rules (always)'))
        table = lambda text: section(text, 'The phases').split('\n### ')[0]  # noqa: E731 (the loop summary changed)
        self.assertEqual(table(self.skill), table(before))
        self.assertEqual(section(self.skill, 'Done means'), section(before, 'Done means'))
        for r in REFS:
            prev = old(f'references/{r}')
            if not prev:
                continue  # new in 0.4.0
            now = read('references', r)
            for h in re.findall(r'(?m)^#{1,3} .+$', prev):
                self.assertIn(h, now, f'heading lost from {r}: {h}')
            lines = {line.strip() for line in now.splitlines()}
            for line in prev.splitlines():
                t = line.strip()
                if t and t not in lines and not any(t.startswith(c) for c in CHANGED_REFS_040):
                    self.assertIn(t, have, f'lost from 0.3.2 {r}: {t}')


if __name__ == '__main__':
    unittest.main()
