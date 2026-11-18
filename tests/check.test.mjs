// Tests for check.mjs's spec parsing and value comparison (no browser needed): node --test tests/
import test from 'node:test';
import assert from 'node:assert/strict';
import { parseSpec, parseProps, compareProps, hexToRgba, unmangle, MARKS } from '../skills/figma-to-wordpress/scripts/check.mjs';

const SPEC = `# home / hero
- box@1440: w=1440 h=760
box@375: w=375 h=812
- el@1440: "Our services" font="Inter Tight" size=40 weight=600 line=48 tracking=-0.8 color=#15202b
- el@375: img.hero-photo w=343 h=257 fit=cover pos="50% 30%"
- el@1440: input[type=email] radius=8
- state@1440: hover .btn-primary bg=#c2321f color=#fff
- state@375: click .menu-toggle => .site-nav ul visible=1
- state@1440: focus "Book now" focusring=1
`;

test('parseSpec reads boxes, elements and states', () => {
  const s = parseSpec(SPEC);
  assert.deepEqual(s.box, { 1440: { w: 1440, h: 760 }, 375: { w: 375, h: 812 } });
  assert.equal(s.el[1440].length, 2);
  assert.deepEqual(s.el[1440][0].target, { text: 'Our services' });
  assert.equal(s.el[1440][0].props.font, 'Inter Tight');
  assert.equal(s.el[1440][1].target.css, 'input[type=email]');
  assert.equal(s.el[1440][1].props.radius, '8');
  assert.deepEqual(s.el[375][0].target, { css: 'img.hero-photo' });
  assert.equal(s.el[375][0].props.pos, '50% 30%');
  assert.equal(s.state[1440][0].action, 'hover');
  assert.deepEqual(s.state[1440][0].check, { css: '.btn-primary' });
  assert.deepEqual(s.state[375][0].on, { css: '.menu-toggle' });
  assert.deepEqual(s.state[375][0].check, { css: '.site-nav ul' });
  assert.equal(s.state[375][0].props.visible, '1');
  assert.deepEqual(s.state[1440][1].on, { text: 'Book now' });
});

test('parseProps and hexToRgba', () => {
  assert.deepEqual(parseProps('a=1 b="x y"'), { a: '1', b: 'x y' });
  assert.deepEqual(hexToRgba('#fff'), [255, 255, 255, 1]);
  assert.deepEqual(hexToRgba('15202b80'), [21, 32, 43, 0.5]);
  assert.equal(hexToRgba('red'), null);
});

test('compareProps passes within the marks and fails outside them', () => {
  const want = { font: 'Inter Tight', size: '40', weight: '600', line: '48', tracking: '-0.8', color: '#15202b' };
  const good = { font: '__Inter_Tight_a1b2c3', size: 40.4, weight: 600, line: 48.9, tracking: -0.75, color: [22, 33, 44, 1] };
  assert.deepEqual(compareProps(want, good, MARKS, 1), []);
  const bad = { ...good, size: 44, weight: 500, color: [40, 32, 43, 1], font: 'Arial' };
  const out = compareProps(want, bad, MARKS, 1);
  assert.equal(out.length, 4);
  assert.match(out.join('|'), /size 44px \(Figma 40px\)/);
});

test('compareProps for images, visibility and focus', () => {
  const want = { w: '343', h: '257', fit: 'cover', pos: 'center top', visible: '1', focusring: '1' };
  const got = { w: 344.5, h: 257, fit: 'cover', pos: '50% 0%', visible: true, focusring: true };
  assert.deepEqual(compareProps(want, got, MARKS, 2), []);
  assert.equal(compareProps(want, { ...got, w: 346, fit: 'fill', visible: false }, MARKS, 2).length, 3);
});

test('unmangle undoes the Git Bash path rewrite', () => {
  assert.equal(unmangle('C:/Program Files/Git/about/'), '/about/');
  assert.equal(unmangle('/about/'), '/about/');
});
