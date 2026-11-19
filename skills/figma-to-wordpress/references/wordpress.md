# The WordPress target

WordPress is built with the **convert-to-wordpress** skill's kit and rules: setup, theme, fields, forms, emails, SEO,
security, launch and live QA. This file does not repeat them. It says where to find them and what differs when the
source is a Figma design instead of an existing website.

## Find the kit

- Installed skill: `~/.claude/skills/convert-to-wordpress/` (a clone of github.com/KuyaLoy/convert-wordpress-skill;
  it has `SKILL.md`, `scripts/`, `assets/`, `references/` and the developer's `profile.local.json`).
- Read its **WordPress essentials**, `references/wordpress-essentials.md` (from its 0.8.0; an older kit: its
  SKILL.md), only the part for the current phase, and use the scripts each item names by path. Not installed: ask
  the developer once where it is, or clone it with their OK.
- Its rules for WordPress itself apply unchanged: plugins, theme and prefix, ACF field model and Theme Settings,
  seeding, Contact Form 7 and the branded emails, spam protection, Yoast, hardening, the client's wp-admin, launch
  and rollback, live QA and the report format.

## Phase 1: setup in one go

Run the kit's setup without stopping at each step (one OK for the whole list of downloads and installs, each named
with its source and size, unless the developer's profile says otherwise):

1. The local site: folder, address and database as the kit's doctor suggests (or the task says).
2. WordPress downloaded and checked, `wp-config.php` written by the kit's scripts (local environment, debug log):
   `scripts/setup/get-wordpress.py` and `make-wp-config.py`.
3. Installed by `scripts/setup/install-wp.py <wp_root> --url <local url> --profile <kit>/profile.local.json` with
   the developer's default local admin from that profile (its `local_admin` entry). Read at run time, used only on
   this local site, never written to any file of the build. No default in the profile: the developer types it.
4. Plugins: ACF PRO from the developer's zip (`plugin_zips.acf_pro`; the developer pastes the licence into
   wp-config), Contact Form 7, Yoast SEO, and the profile's `required` extra plugins. Not locally: the WebP
   conversion plugin and Contact Form CFDB7 (they go on live at launch).
5. The theme, by the starter rule (the plan states the choice and one reason; the developer can override; the
   task's word wins). A Figma design is never a Tailwind source, so:
   - **clearly easier in Tailwind** (a design system with repeating tokens: Figma variables or styles, many
     reusable sections and components): the kit's Tailwind starter, **_tw**;
   - **a normal site that doesn't really need Tailwind** (small, mostly one-off layouts, plain CSS expected):
     **Barebones** with CSS-variable tokens.
   Prepared by the kit (its setup names both). Activate it, build its assets, PHPCS clean (SKILL.md rule 13).
6. Tokens: `_figma/tokens.json` becomes the theme's tokens: on _tw the Tailwind `@theme` block, on Barebones CSS
   variables in one tokens file (colours, fonts, type scale, radii, shadows, spacing, container). Fonts
   self-hosted in the theme (`font-display: swap`, only the weights used, the LCP font preloaded).
7. Permalinks `/%postname%/`, the site's language and timezone, "Discourage search engines" on (local only).
8. `_figma/.htaccess` with `Require all denied`; check it answers 403.

Phase 1's QA: the site loads, admin works, plugins active, no notices in debug.log, tokens render (a quick test
page with the type scale and colours, deleted after), `_figma/` answers 403.

## Phase 2: sections become fields

- Every page is a WordPress page (URLs at the root). Pages that share a layout get a fixed template; one-off pages
  use one Flexible Content field ("Page Sections") whose layouts are the sections.
- Build each section as a template part with `data-section="<slug>"` on its root (the check script finds it there).
  Markup from the spec; fields from the start; seeded with the Figma copy verbatim, so the page shows the design
  right after seeding. Anything used on two pages (phone, address, CTA, footer, social links) lives in Theme
  Settings.
- Field names editors understand (labels in plain words, instructions where needed, defaults from Figma).
- Images go into the Media Library and into their fields (never hard-coded); the theme prints them with
  `wp_get_attachment_image()` and correct `sizes`, the LCP image with `fetchpriority="high"` and no lazy loading.
- Global parts: header, footer, menus (WordPress menus), mobile menu (a gap in most files: built from the design
  system), pop-ups and banners as in Figma.
- Thank-you and 404 always exist, from the design's parts when Figma lacks them.

## Phase 3: forms and email

The kit's forms and email rules apply as they are (Contact Form 7 holding each form and its email, the theme printing
the form as the design shows it, branded HTML emails for the notification and the auto-reply, spam protection,
thank-you redirect). The form's look comes from the Figma spec: fields, labels, errors and success states (states
Figma lacks are built from the design system and listed).

## Phase 4: SEO, security, speed

The kit's SEO and security rules apply (Yoast seeded, schema, canonicals, noindex thank-you, redirects for old URLs
if the site replaces one, hardening, private files 403). Speed: built in from the first section (rule 6 of
SKILL.md). A heavy design (background video, large imagery, many animations) may get one speed plugin that fits
the host (for example LiteSpeed Cache on a LiteSpeed host, otherwise a cache and asset plugin the developer uses);
set it up after the build is final, check the design is unchanged at 1440 and 375, and list it.

## Live

The kit's launch steps, one at a time, with the developer doing every step that needs a password or a payment.
After the move: the WebP conversion plugin (Converter for Media unless the developer names another) and Contact
Form CFDB7 installed and active on live; the kit's live plugins; search engines allowed; debug off; live QA.
