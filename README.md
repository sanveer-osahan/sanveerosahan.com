# sanveerosahan.com

Personal website and blog of Sanveer Osahan. Built with [Astro](https://astro.build/) and the [AstroPaper](https://github.com/satnaing/astro-paper) theme. Deployed on Cloudflare Pages.

## Development

```bash
pnpm install
pnpm dev      # http://localhost:4321
pnpm build    # production build → dist/
```

## Writing a post

Add a markdown file to `src/content/posts/`:

```markdown
---
title: Post Title
author: Sanveer Osahan
pubDatetime: 2026-06-05T12:00:00.000+05:30
slug: post-slug
featured: false
draft: false
tags:
  - tag
description: "One-line description."
timezone: "Asia/Kolkata"
---

Content here.
```

`draft: true` hides a post from the live site. Push to `main` → Cloudflare Pages auto-deploys.

## Site config

- `astro-paper.config.ts` — title, author, socials, features
- `src/content/pages/about.md` — about page
- `src/pages/index.astro` — homepage hero

## Credits

Theme: [AstroPaper](https://github.com/satnaing/astro-paper) by Sat Naing (MIT — see LICENSE).
