# Context map

This repo has more than one context. This file is the index.

## Site-wide

[`CONTEXT.md`](./CONTEXT.md) covers identity, positioning, voice, and the content model (Post, Draft, Name, Tagline, Video companion). It applies everywhere.

## Per-post

Each Post has its own context under `docs/context/posts/<slug>.md`, named to match the Post's slug in `src/content/posts/`. Post-local vocabulary and decisions (audience, hook, framing, terms specific to that piece) live there, not in the site-wide file.

Post contexts stay out of `src/content/posts/` on purpose. That directory is globbed as the published collection, so a stray `.md` there would ship as a live post.

- [`docs/context/posts/set-up-your-ai-coding-agent.md`](./docs/context/posts/set-up-your-ai-coding-agent.md): "Set Up your AI Coding Agent: From Premium to Free"
