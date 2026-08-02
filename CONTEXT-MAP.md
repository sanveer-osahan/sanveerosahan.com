# Context map

This repo has more than one context. This file is the index.

## Site-wide

[`CONTEXT.md`](./CONTEXT.md) covers identity, positioning, voice, and the content model (Article, Note, Draft, Name, Tagline, Video companion). It applies everywhere.

## Per-article

Each Article has its own context under `docs/context/articles/<slug>.md`, named to match the Article's slug in `src/content/articles/`. Article-local vocabulary and decisions (audience, hook, framing, terms specific to that piece) live there, not in the site-wide file.

Article contexts stay out of `src/content/articles/` on purpose. That directory is globbed as the published collection, so a stray `.md` there would ship as a live article. The same trap applies to `src/content/notes/`, and more sharply, because Notes have no draft flag to hide behind.

- [`docs/context/articles/set-up-your-ai-coding-agent.md`](./docs/context/articles/set-up-your-ai-coding-agent.md): "Set Up your AI Coding Agent: From Premium to Free"

## Per-note

None. A Note is short enough that its context is the Note itself.
