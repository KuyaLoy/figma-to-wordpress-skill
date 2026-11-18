# The Next.js target

Used when the task asks for Next.js (or the developer chooses it at intake). Same phases, QA and progress page as
WordPress; only the stack differs.

## Phase 1: setup

- `npx create-next-app@latest <name> --ts --tailwind --eslint --app --src-dir --import-alias "@/*"` (ask before the
  install; it downloads packages). Node LTS. Commit the fresh app before any change.
- Tokens: `_figma/tokens.json` becomes Tailwind's theme. Tailwind 4: an `@theme` block in `src/app/globals.css`
  (`--color-brand: #f5412c; --font-sans: var(--font-inter); --text-h1: 3.5rem; --text-h1--line-height: 4rem; ...`).
  Tailwind 3: `tailwind.config.ts` `theme.extend`. Utilities on tokens; custom CSS only where utilities can't.
- Fonts: `next/font/google` (or `next/font/local` for licensed files) with `display: 'swap'`, exposed as CSS
  variables and mapped in the theme. Only the weights Figma uses.
- Container: the designed desktop width (often 1440) as the max width, centred; sections that bleed to the edge in
  Figma keep their full-width background.
- Lint and type check clean: `npm run lint`, `npx tsc --noEmit`.

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
Domain and redirects as the task says. Live QA as in SKILL.md.
