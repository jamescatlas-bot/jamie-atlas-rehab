# Jamie Atlas Rehab & Performance

Production site for [jamieatlas.com](https://www.jamieatlas.com), built with **Astro 5 + Tailwind CSS 4 + Vercel**.

## Stack

- **Framework:** Astro 5 (static-first, near-zero JS by default)
- **Styling:** Tailwind CSS 4 (CSS-first config)
- **Content:** Markdown files in `src/content/`
- **Hosting:** Vercel (auto-deploys from GitHub main branch)
- **DNS:** Cloudflare (when domain is cut over)
- **Forms:** Formspree / Web3Forms (TODO)
- **Booking:** Calendly embed

## Local development

```bash
npm install
npm run dev
```

Visits at `http://localhost:4321`.

## Deployment

Every push to `main` auto-deploys to Vercel.

## Editing content

- **Site-wide config** (phone, email, hours, etc.): `src/data/site.ts`
- **Pages** (Home, About, etc.): `src/pages/*.astro`
- **Condition sub-pages**: `src/pages/what-we-treat/*.astro`
- **Blog/resources** (long-form content): `src/content/resources/*.md` (TODO: set up content collection)

## Important constraints

- Jamie is NOT a licensed physical therapist. Don't use language that claims he is. He IS a Cognitive Functional Therapist + NSCA-CSCS + NASM-CPT.
- All medical claims need to be evidence-backed and conservative.
- Phone number is Google Voice business line: `(720) 257-9328`. NOT Jamie's personal cell.

## File map

```
jamie-atlas-rehab/
├── package.json
├── astro.config.mjs
├── tsconfig.json
├── public/
│   └── favicon.svg
└── src/
    ├── components/
    │   ├── Header.astro
    │   └── Footer.astro
    ├── layouts/
    │   └── BaseLayout.astro
    ├── pages/
    │   └── index.astro
    ├── styles/
    │   └── global.css
    └── data/
        └── site.ts
```
