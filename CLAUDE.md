# sanveerosahan.com

Personal website + **book-notes blog** of Sanveer Osahan. Astro + **Astro Sienna** theme (serif, paper-cream,
hand-drawn diagram support), pnpm, deployed to Cloudflare Pages via GitHub Actions
(`.github/workflows/deploy.yml`).

## Commands

- `pnpm dev` — dev server at localhost:4321
- `pnpm build` — production build (`astro check && astro build`; type errors fail it)
- `pnpm lint` — Biome lint

## Structure

- `src/site.config.ts` — site title, author, description, `profile`, `menuLinks`, expressive-code options
- `astro.config.ts` — `site` URL, integrations, markdown pipeline
- `src/content/post/*.md` — blog posts (`draft: true` hides). Frontmatter: `title`, `publishDate`,
  `description` (10–160 chars), `tags`, optional `draft`/`updatedDate`/`coverImage`
- `src/content/page/about.md` — about page (frontmatter: `title`, `description`)
- `src/layouts/Base.astro` — global shell + theme-aware Mermaid loader
- `src/layouts/BlogPost.astro` — post layout + post-content CSS (handwriting headings, diagram frames)
- `src/components/BaseHead.astro` — `<head>` incl. Cloudflare Web Analytics beacon

## Diagrams (the "sloppy" / hand-drawn look)

- **Mermaid handDrawn** — author a raw `<pre class="mermaid">…</pre>` block in a post (NOT a ```mermaid fence,
  so expressive-code ignores it). `Base.astro` bundles Mermaid (code-split, loads only on pages with diagrams),
  renders `look: "handDrawn"`, and **re-colors on light/dark toggle** via the `theme-change` event.
- **Excalidraw (theme-swap images)** — upload two files per diagram to `public/diagrams/`
  (`<name>-light.svg` + `<name>-dark.svg`) and use:
  ```html
  <figure class="excalidraw">
    <img class="diagram-light" src="/diagrams/<name>-light.svg" alt="…" />
    <img class="diagram-dark"  src="/diagrams/<name>-dark.svg"  alt="" aria-hidden="true" />
    <figcaption>…</figcaption>
  </figure>
  ```
  CSS in `BlogPost.astro` shows the file matching the active theme.
- **Inline SVG** (e.g. the atomic-habits Fig 1) — any `<figure class="diagram">` gets the wobbly frame; use
  `stroke="currentColor"` so it follows the theme.
- Sketchy callout: `<aside class="sketch-note"><strong>Title</strong> …</aside>`.

## Conventions

- Push to `main` → auto-deploy. No direct wrangler deploys from local.
- This is a PERSONAL project — personal GitHub account (`sanveer-osahan`), not AtlanHQ.
- `package.json` `pnpm.onlyBuiltDependencies` whitelists esbuild/sharp/biome so CI's frozen install builds them.

## Agent skills

### Issue tracker

Issues are tracked as GitHub Issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default triage vocabulary (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context (one CONTEXT.md + docs/adr/ at the repo root). See `docs/agents/domain.md`.
