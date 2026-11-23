# The Next.js target

Used when the task asks for Next.js (or the developer chooses it at intake). Same phases, QA and progress page as
WordPress; only the stack differs.

## Phase 1: setup

- `npx create-next-app@latest <name> --ts --tailwind --eslint --app --src-dir --import-alias "@/*"` (ask before the
  install; it downloads packages). Node LTS. Commit the fresh app before any change.
- Tokens: `_figma/tokens.json` becomes Tailwind's theme. Tailwind 4: an `@theme` block in `src/app/globals.css`
  (`--color-brand: #f5412c; --font-sans: var(--font-inter); --text-h1: 3.5rem; --text-h1--line-height: 4rem; ...`).
  Tailwind 3: `tailwind.config.ts` `theme.extend`. Utilities on tokens; custom CSS only where utilities can't. A
  value with no token gets one; no arbitrary values (`text-[19px]`, `bg-[#...]`) and no hex outside the theme.
- Fonts: `next/font/google` (or `next/font/local` for licensed files) with `display: 'swap'`, exposed as CSS
  variables and mapped in the theme. Only the weights Figma uses.
- Container: the designed desktop width (often 1440) as the max width, centred; sections that bleed to the edge in
  Figma keep their full-width background.
- Lint, format and type check clean at every phase gate: `npm run lint` (ESLint), `npx prettier --check .`
  (Prettier added as a dev dependency with `prettier-plugin-tailwindcss`), `npx tsc --noEmit`. Remove the
  starter's demo files and assets the site doesn't use (SKILL.md rule 13).

## Phase 2: pages

- App Router: one folder per route under `src/app/`, the URLs from the task or the menu in Figma. Global parts in
  `src/components/site/` (header, footer, mobile menu), sections in `src/components/sections/`.
- Server Components by default; `'use client'` only for the interactive part (menu toggle, slider, accordion), kept
  as small as possible.
- Content: one typed file per page in `src/content/` (the Figma copy verbatim), unless the task names a CMS; then
  the CMS's schema follows the same sections.
- Images: `next/image` with the real `width` and `height`, `sizes` matching the layout at each breakpoint,
  `priority` (and `fetchPriority="high"`) only on the LCP image, everything else lazy. Assets in `public/images/`.
- SVG icons as components or files, keeping their width and height.
- Carousels: Swiper (`swiper/react`), imported only in the client component that uses it.
- Video: `<video muted playsInline preload="metadata" poster=...>`; autoplay only where Figma shows it playing.

## Phase 3: forms and email

- A Server Action (or `app/api/<form>/route.ts`) with schema validation (zod), a honeypot field, and the spam
  protection the task names (reCAPTCHA v3 or Cloudflare Turnstile). The keys go in environment variables the
  developer sets; `.env.local` is never committed, `.env.example` lists the names only.
- Mail through the task's service (Resend, SMTP, the client's provider). HTML email built from the design's colours
  and logo; a plain-text part too. Redirect to `/thank-you` (noindex) where the conversion fires.
- Without JavaScript the form still posts (progressive enhancement with a Server Action).
- **Where the lead came from (form attribution),** on every lead form by default, no package; the same names, caps,
  email row and event as convert-to-wordpress 0.9.9 (its `references/forms-email.md` > Where the lead came from):
  - **Browser, first party only** (`src/lib/attribution.ts`, a small client module loaded once in the root layout):
    last touch per visit in sessionStorage `kitwp_attr_last` (the campaign tags `utm_source`, `utm_medium`,
    `utm_campaign`, `utm_term`, `utm_content`, the ad click ids `gclid`, `gbraid`, `wbraid`, `fbclid`, `msclkid`,
    `landing_page`, `referrer`; a new campaign link replaces them); first touch in localStorage `kitwp_attr_first`
    for 90 days (`first_source`, `first_medium`, `first_campaign`, `first_landing_page`, `first_referrer`,
    `first_seen` YYYY-MM-DD). Addresses keep host and path, never the query. Nothing leaves the browser until the
    visitor sends a form; nothing goes to a third party. Storage blocked: the form still gets this page's values.
  - **Consent as the kit's "auto":** Google Consent Mode in the dataLayer. A page that sets a consent default has
    a banner: the first visit goes to localStorage only once `ad_storage` or `analytics_storage` is granted; until
    then, and after an update with neither granted, only this visit is kept (sessionStorage), and a decline removes
    a stored first visit. No consent default on the page: no banner, stored as above. Either way the form gets this
    visit's values.
  - **Hidden fields on every lead form** with those 18 names, filled at load, on first focus and at submit.
  - **Checked on the server** (`src/lib/attribution-server.ts`, `import 'server-only'`, called by every form's
    action): only those names, strings, cleaned, capped (500 for `landing_page`, `referrer`, `first_landing_page`,
    `first_referrer`; 10 for `first_seen`; 200 for the rest), http(s) addresses with host and path only; anything
    else dropped. Without JavaScript the form page's own address (the `Referer` header) gives its campaign tags and
    click ids. Reporting only: never used to decide anything about a lead.
  - **The lead email:** a "Where this lead came from:" row (HTML escaped, and in the plain-text part): Source /
    medium, Campaign, Keyword, Ad content, Ad click (Google Ads (gclid), Meta (fbclid), Microsoft Ads (msclkid)...),
    Referrer, Landing page, First visit; empty lines dropped; "Direct (no campaign, ad click or other site)" when
    none.
  - **The conversion:** at submit the form's client part stores the form's name, source, medium and the time in
    sessionStorage `kitwp_lead`; `/thank-you` pushes one `generate_lead` to the dataLayer with `form_name`,
    `lead_source` and `lead_medium` when that entry is under 30 minutes old, then removes it, so a refresh or a
    direct visit pushes nothing.
- **The leads portal** (mandatory on live for every lead form; a site without one says so in the plan): a
  server-only `sendLead()` in `src/lib/leads.ts` (`import 'server-only'`), called from each form's action
  **whether the mail service succeeded or failed**, once per submission:
  - `POST` JSON to `process.env.LEADS_ENDPOINT` with `Authorization: Bearer ${process.env.LEADS_WRITE_KEY}`:
    `form` (the form's name), a unique `idempotency_key` (`crypto.randomUUID()`), the posted fields, `source_url`,
    `ip_address` (from `x-forwarded-for`), the cleaned attribution fields under the same names (`gclid` from the
    visit), `fbp`, `fbc` (from the `_fbp`/`_fbc` cookies). Never files, consent, the honeypot or sensitive fields
    (health, dates of birth).
  - A 5 second timeout (`AbortSignal.timeout(5000)`); 200 and 202 count as delivered; any failure is logged with the
    status only and never blocks the visitor or the thank-you page.
  - Off unless both variables are set: they are set only for the live (Production) environment on the host, never
    in `.env.local` or preview deployments. `.env.example` lists the two names only.
  - The portal's own Next.js example (in its admin) is the reference; the portal's address comes from the
    developer's profile or the task, never from this skill.

## Phase 4: SEO, security, speed

- Metadata API: `metadata` or `generateMetadata` per route (title, description, canonical, Open Graph, Twitter);
  `app/sitemap.ts`, `app/robots.ts`; JSON-LD in a `<script type="application/ld+json">` per page where it fits
  (Organization or LocalBusiness, BreadcrumbList, FAQPage only with answers).
- `/thank-you` noindex and out of the sitemap; a real `not-found.tsx` with the design's parts.
- Security headers in `next.config.ts` (`X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options` or CSP
  `frame-ancestors`, `Permissions-Policy`); no secrets in client code (`NEXT_PUBLIC_` only for public values).
- Speed: `next build` with no warnings; check the bundle for anything heavy; `next/script` with `lazyOnload` or
  `afterInteractive` for third-party scripts (GTM per the task); PageSpeed Insights on the deployed preview.

## Live

Deploy where the task says (Vercel by default: the developer connects the repo and sets the environment variables).
Domain and redirects as the task says. The leads portal: the project in the portal admin (domain = the live domain),
`LEADS_ENDPOINT` and `LEADS_WRITE_KEY` set for Production only, then the GET check, which stores nothing (the
convert-to-wordpress kit's `scripts/report/leads-check.py` works for any site; the developer runs it with the key
from the environment or its hidden prompt), then one TEST lead per form after the developer agrees (one from a page
opened with `?utm_source=qa&utm_medium=test&utm_campaign=launch&gclid=TEST`: the email row and the portal show
them; a lead from a plain visit shows "Direct"). Live QA as in SKILL.md.
