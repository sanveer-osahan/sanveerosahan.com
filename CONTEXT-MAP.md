# Context map

This repo has more than one context. This file is the index.

## Site-wide

[`CONTEXT.md`](./CONTEXT.md) covers identity, positioning, voice, and the content model (Article, Note, Reading, Book, Draft, Name, Tagline, Video companion). It applies everywhere.

## Per-article

Each Article has its own context under `docs/context/articles/<slug>.md`, named to match the Article's slug in `src/content/articles/`. Article-local vocabulary and decisions (audience, hook, framing, terms specific to that piece) live there, not in the site-wide file.

Article contexts stay out of `src/content/articles/` on purpose. That directory is globbed as the published collection, so a stray `.md` there would ship as a live article. The same trap applies to `src/content/notes/`, and more sharply, because Notes have no draft flag to hide behind.

- [`docs/context/articles/set-up-your-ai-coding-agent.md`](./docs/context/articles/set-up-your-ai-coding-agent.md): "Set Up your AI Coding Agent: From Premium to Free"
- [`docs/context/articles/support-tickets-as-a-data-product.md`](./docs/context/articles/support-tickets-as-a-data-product.md): "Support Tickets as a Data Product: Building the Analysis Layer on Databricks"

## Datasets

- [`docs/databricks/DATA-MODEL.md`](./docs/databricks/DATA-MODEL.md): the synthetic support ticket dataset behind that article.

## Per-note

None. A Note is short enough that its context is the Note itself.

## Per-reading

None. A Reading takes its framing from the book it covers, so there is no local vocabulary to record.

The same trap as above applies to `src/content/bookshelf/`: that directory is the published collection. A Reading has a `draft` flag to hide behind, so a stray file there is less dangerous than one in the Notes folder, but it still needs `draft: true` to stay off the site.
