"""0.4.1: the company attribution standard and the agency badge (convert-to-wordpress 0.12.0). WordPress builds point
to the kit's sections and copy nothing; Next.js builds carry the same eleven labelled fields in the lead email and
the same badge rule (dynamic, with its link), with no CRM or app connection yet."""
import os
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SKILL_DIR = os.path.join(ROOT, 'skills', 'figma-to-wordpress')
LABELS = ('Lead Source', 'Google Ads Campaign ID', 'Google Click ID', 'Landing Page', 'Referrer', 'Lead Source Date',
          'Form Submitted From', 'First Touch Source', 'First Visit Date', 'First Touch Landing Page',
          'First Touch Referrer')


def read(*parts):
    with open(os.path.join(SKILL_DIR, *parts), encoding='utf-8') as fh:
        return fh.read()


def flat(text):
    return ' '.join(text.split())


class Attribution041(unittest.TestCase):
    skill = flat(read('SKILL.md'))
    wp = flat(read('references', 'wordpress.md'))
    nx = flat(read('references', 'nextjs.md'))

    def test_skill_names_the_rule_under_the_limit(self):
        self.assertLess(len(read('SKILL.md').encode('utf-8')), 19000)
        self.assertIn('## Every site, whatever the design shows', self.skill)
        for s in ('agency badge with its link', "client's recorded request", 'eleven labelled attribution fields',
                  '`references/wordpress.md` (convert-to-wordpress 0.12.0 or later)', '`references/nextjs.md`'):
            self.assertIn(s, self.skill)

    def test_wordpress_points_to_the_kit(self):
        for s in ('`references/build.md` > Agency badge, 0.12.0 or later',
                  '`references/forms-email.md` > Where the lead came from, 0.12.0 or later',
                  '`references/forms-email.md` > Form layout (0.12.0 or later)',
                  '> The auto-reply and the agency badge (0.12.0 or later)', '(class `branding`)', '(check 11)',
                  "the app the profile's connector plugin feeds (its > The CRM or app)"):
            self.assertIn(s, self.wp)
        for label in LABELS[1:]:
            self.assertNotIn(label, self.wp, 'the standard is pointed to, not copied')

    def test_nextjs_same_fields_and_badge(self):
        self.assertIn('The labels, in this order: ' + ', '.join(LABELS) + '.', self.nx)
        for s in ('convert-to-wordpress 0.12.0', 'Lead Attribution table', '`agencyBadge` (image, link, alt)',
                  "footer's bottom bar", "its `hide` works only with the task's note that the client asked",
                  'both end with the agency badge, linked', 'a PNG at 2x',
                  'No CRM or app connection for Next.js builds yet', '`gad_campaignid`', '`first_gad_campaignid`',
                  '`utm_id`', '`first_id`'):
            self.assertIn(s, self.nx)
        self.assertNotIn('Lead source table', self.nx)

    def test_checks_carry_it(self):
        steps = flat(read('references', 'phase-steps.md'))
        qa = flat(read('references', 'qa.md'))
        live = flat(read('references', 'live.md'))
        for text in (steps, qa):
            self.assertIn('?gad_campaignid=123&gclid=TEST&utm_source=google', text)
            self.assertIn('eleven Lead Attribution rows in order', text)
            self.assertIn('agency badge', text)
        self.assertIn("eleven rows in the email's Lead Attribution table", live)
        self.assertIn('`live-qa.py` check 11', live)


if __name__ == '__main__':
    unittest.main()
