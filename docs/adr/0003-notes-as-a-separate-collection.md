# Notes as a separate collection, and Posts renamed to Articles

## Status

accepted. Supersedes [ADR-0001](./0001-single-posts-collection.md).

## Context

ADR-0001 put every piece of writing into one broad `posts` collection and said
to split "when the volume of one kind earns its own type". Four short pieces
arrived at once: standalone thoughts with no title, no description, and no
reason to have a page of their own. They are meant to be read as a wall of
cards, three across, not as a list of links.

Forcing them into the Post schema would mean four files carrying a `title` and
`description` that nothing renders, and every existing query growing a filter.
That is the trigger ADR-0001 described.

## Decision

Two collections.

- `articles` at `/articles/<slug>/`. The old `posts` collection, renamed, schema
  unchanged: `title`, `description`, `publishDate`, `draft`, `tags[]`, optional
  `videoUrl`.
- `notes` at `/notes/`, schema `publishDate` only. The body is the whole Note.
  Notes have no individual pages. Each card carries an `id`, so a single Note is
  linkable at `/notes/#<slug>` through a permalink mark revealed on hover.

The URL moved with the name. `/posts/` becomes `/articles/`, and
`public/_redirects` holds `/posts/* /articles/:splat 301`.

## Why

The two types have genuinely different shapes, so one schema could only serve
both by leaving fields empty. A Note has no title because a title would be
longer than some of the Notes.

The rename was chosen over keeping `/posts/` as a URL alias for the label
"Articles". A nav that reads one thing and points at another is a permanent
papercut, and `/articles/` and `/notes/` as siblings is the shape the site keeps
for years. The one published Article was two days old when this was decided, so
the redirect covers a nearly empty blast radius.

`draft` was deliberately left off the Notes schema. A Note is short enough to
finish in one sitting, so the staging mechanism Articles need has no job here.

`tags[]` was deliberately left off too. ADR-0001's own consequences recorded
that `tags[]` on posts is "inert metadata until filtering is built", and it has
stayed inert since. Adding a second never-read field to a brand new type repeats
a mistake already written down.

## Consequences

- For a Note, the folder is the publish switch. Any `.md` file under
  `src/content/notes/` is live on the wall and in the sitemap immediately.
  Unfinished Notes must live somewhere else.
- Note cards show month and year, never the day. The day and time in
  `publishDate` are therefore free ordering control: several Notes published on
  the same day can be sequenced exactly by time, invisibly to readers.
- The Notes wall uses equal-height rows, so one long Note inflates its whole
  row. The 150 word guidance in `CONTEXT.md` is a layout constraint as much as a
  vocabulary one, and nothing enforces it.
- `public/_redirects` is a permanent file. It is the only reason the original
  Article URL still resolves, so it outlives the rename that caused it.
- `docs/context/posts/` moved to `docs/context/articles/` and the docs that
  discuss writing were reworded from "post" to "article".
- Asset paths under `public/images/posts/<slug>/` keep the old word on purpose.
  They are live URLs on the CDN, so renaming them would break cached references
  and social card images to buy nothing a reader ever sees. The word "post"
  survives there and nowhere else.
