# sanveerosahan.com

Personal website of Sanveer Osahan. Astro + **Astro Sienna** theme (serif, paper-cream, light/dark),
stripped to a minimal **Home + About** site. pnpm, deployed to Cloudflare Pages via GitHub Actions
(`.github/workflows/deploy.yml`).

## Commands

- `pnpm dev` — dev server at localhost:4321
- `pnpm build` — production build (`astro check && astro build`; type errors fail it)
- `pnpm lint` — Biome lint

## Structure

- `src/site.config.ts` — site title, author, description, `menuLinks`
- `astro.config.ts` — `site` URL, integrations (tailwind, sitemap, robots, webmanifest, compress)
- `src/pages/index.astro` — Home page
- `src/pages/about.astro` — About page
- `src/pages/404.astro` — not-found page
- `src/layouts/Base.astro` — global shell (BaseHead, header, footer, theme toggle, skip link)
- `src/components/BaseHead.astro` — `<head>` incl. meta, favicons, and Cloudflare Web Analytics beacon
- `src/components/layout/` — `Header.astro`, `Footer.astro`
- `src/components/ThemeToggle.astro` / `ThemeProvider.astro` — light/dark toggle
- `src/styles/global.css` — Sienna theme styles

## Conventions

- Push to `main` → auto-deploy. No direct wrangler deploys from local.
- This is a PERSONAL project — personal GitHub account (`sanveer-osahan`), not AtlanHQ.
- `package.json` `pnpm.onlyBuiltDependencies` whitelists esbuild/sharp/biome so CI's frozen install builds them.
- Home and About are intentionally minimal placeholders for now.
