# sanveerosahan.com

Personal website + blog of Sanveer Osahan. Astro + AstroPaper v6 theme, pnpm, deployed to Cloudflare Pages via GitHub Actions (`.github/workflows/deploy.yml`).

**If `SETUP.md` exists, initial launch is incomplete — read it and continue from the first unchecked step.**

## Commands

- `pnpm dev` — dev server at localhost:4321
- `pnpm build` — production build (runs `astro check`; type errors fail it)

## Structure

- `astro-paper.config.ts` — site title, author, socials, features
- `src/content/posts/*.md` — blog posts (`draft: true` hides)
- `src/content/pages/about.md` — about page
- `src/pages/index.astro` — homepage hero

## Conventions

- Posts: markdown, frontmatter per README.md "Writing a post"
- Push to `main` → auto-deploy. No direct wrangler deploys from local.
- This is a PERSONAL project — personal GitHub account, not AtlanHQ.
