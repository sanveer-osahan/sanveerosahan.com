# sanveerosahan.com

Personal website of Sanveer Osahan. Built on [Astro](https://astro.build) with the
[Astro Sienna](https://github.com/AnjayGoel/astro-sienna) theme (stripped to a minimal Home + About).
Deployed to Cloudflare Pages via GitHub Actions.

## Development

```bash
pnpm install   # or: corepack pnpm install
pnpm dev       # dev server at localhost:4321
pnpm build     # astro check && astro build
pnpm lint      # Biome lint
```

## Structure

- `src/site.config.ts` — title, author, description, `menuLinks`
- `astro.config.ts` — `site` URL, integrations
- `src/pages/index.astro` — Home
- `src/pages/about.astro` — About
- `src/layouts/Base.astro` — global shell (header, footer, theme toggle)
- `src/styles/global.css` — Sienna theme styles (serif, paper-cream, light/dark)

## Deployment

Push to `main` → GitHub Actions builds and deploys to Cloudflare Pages
(`.github/workflows/deploy.yml`, project `sanveerosahan-com`).
