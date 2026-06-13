# Distinct content collections per content type

The site models Book Notes, Blog Posts, How-to Guides, and Videos as four separate content
collections, each with its own schema and route (`/books`, `/blog`, `/guides`, `/videos`), rather
than one `post` collection differentiated by a `category` tag. We chose this because the types have
genuinely different shapes — a Book Note requires book metadata (author, cover, Amazon link), a
Video requires a YouTube link and carries published prep/show-notes, and a How-to Guide carries
optional procedural fields — and per-collection schemas let the build enforce those differences
instead of leaving them as conventions on a shared type.

## Considered Options

- **One `post` collection + `category` field** (rejected): simpler, but no per-type schema
  enforcement (nothing stops a "book note" with no Amazon link), and weaker routing/navigation.

## Consequences

- `tags` is the only cross-type grouping mechanism; there is deliberately no separate "Category" concept.
- A `Video` references the piece it was derived from via an optional `relatedTo` link, which crosses
  collection boundaries and needs handling at build time.
