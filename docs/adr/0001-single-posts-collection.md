# Single `posts` collection over typed content collections

## Status

superseded by [ADR-0003](./0003-notes-as-a-separate-collection.md)

The split this ADR anticipated ("split when the volume of one kind earns its own
type") happened. Notes became their own collection and `posts` was renamed to
`articles`. The reasoning below is kept because it is why the split waited.

## Context

An earlier scaffold defined separate `book`, `guide`, and `video` content collections, with its own ADR, before any content existed. All of it was stripped back to a bare Home + About site. Re-adding writing now, we have exactly one Post to publish.

## Decision

One `posts` collection under `/posts/<slug>`. Every piece of writing is a Post, whatever its kind. A Post that pairs with a YouTube video carries an optional `videoUrl`; the video is metadata on the Post, not a separate type. Schema is `title`, `description`, `publishDate`, `draft`, `tags[]`, and optional `videoUrl`.

## Why

Typing content by kind before knowing the mix produced structure that was never used and then deleted. Splitting a broad collection later (once one kind clearly dominates) is a mechanical migration. Guessing the taxonomy up front is not. Start with the broad noun, split when the volume of one kind earns its own type.

## Consequences

- `tags[]` exists in the schema but has no tag pages yet. Inert metadata until filtering is built.
- Drafts are excluded from production builds and the sitemap; the Posts nav link renders only when a published post exists, so production never shows a dead link or an orphan page.
