# Notes wall, and Posts renamed to Articles

Design spec. Decided 2026-08-02. Architectural record in
[ADR-0003](../../adr/0003-notes-as-a-separate-collection.md).

## Goal

Add a dedicated page for short standalone thoughts, shown as one card per row.
Rename the existing Posts section to Articles. Surface the newest three Notes on
the home page.

The wall started as a three-column grid during design (see the card-style and
homepage mockups referenced below) and moved to a single column after
comparing 3-up, 2-up, and 1-up with real content live in the dev server. The
single column read better for text this dense, and it removed the
equal-height-row problem the 3-up grid was designed around, since a lone card
in a row has no neighbor to leave dead space next to.

## Domain model

Two content types where there was one. Full definitions live in
[`CONTEXT.md`](../../../CONTEXT.md).

- **Article**: titled long-form writing at `/articles/<slug>/`. The old Post,
  renamed. Schema unchanged.
- **Note**: one idea, self-contained, read in a single breath. No title, no
  headings, roughly 150 words or less. Always Sanveer's own words. Lives only as
  a card on the wall at `/notes/`, anchored at `/notes/#<slug>`.

The boundary: if a piece needs a title to make sense, or wants headings, it is
an Article. Judgment only. Nothing in the build enforces it.

## Content model

### `articles` collection

Renamed from `posts`. Schema unchanged:

```ts
{
  title: string
  description: string
  publishDate: Date
  draft: boolean = false
  tags: string[] = []
  videoUrl?: string (url)
}
```

### `notes` collection

```ts
{
  publishDate: Date
}
```

One field. The body is the entire Note.

No `draft`, so any `.md` under `src/content/notes/` is live on the wall and in
the sitemap the moment it exists. Unfinished Notes live outside that folder.

No `tags[]`. ADR-0001 recorded that `tags[]` on posts is inert metadata, and it
has stayed inert. A second never-read field is not added.

Cards render month and year only, so the day and time in `publishDate` are free
ordering control. Notes published on the same day are sequenced by time, which
readers never see.

## Routing

| Route | Renders |
| --- | --- |
| `/articles/` | Article index, existing treatment, heading "Articles" |
| `/articles/<slug>/` | Single Article, existing treatment |
| `/notes/` | The wall. Every Note, newest first, full text |
| `/notes/#<slug>` | Same page, scrolled to one card |

Notes have no individual pages. `/notes/` adds exactly one URL to the sitemap
regardless of how many Notes exist.

`public/_redirects` (new file):

```
/posts/*  /articles/:splat  301
```

Cloudflare Pages serves this on a static build. No Astro config change needed.
There are no internal markdown links to `/posts/`, so the redirect exists purely
for external links to the one published Article.

## Components

### `src/components/NoteWall.astro`

The only place a note card is defined. Used by both pages.

```ts
interface Props {
  notes: CollectionEntry<"notes">[]
  permalinks?: boolean   // default false
}
```

Renders a CSS grid of cards. Each card is an `<article id={note.id}>`. Body
comes from `render(note)`. When `permalinks` is true, each card footer gets an
anchor to `#{note.id}`.

### Card anatomy

Index card. Values reuse existing tokens from `global.css`; no new ones.

| Property | Value |
| --- | --- |
| background | `var(--paper)` (`#fbf6ec` light, `#1a1715` dark) |
| border | `1px solid var(--hairline)` |
| top border | `3px solid hsl(var(--theme-accent))` |
| radius | `3px` |
| padding | `22px 22px 16px` |
| shadow | `0 2px 6px -3px` at low opacity |
| body | `var(--font-serif)`, no font-size override, `hsl(var(--theme-text-muted))` |
| footer | pinned with `margin-top: auto` |
| date | `var(--font-sans)`, 12px, `hsl(var(--theme-text) / 0.45)`, format `"August 2026"` |
| permalink | `№`, `hsl(var(--theme-accent))`, `opacity: 0` rising to `0.75` on `:hover` and `:focus-within` |

Date format is `Intl.DateTimeFormat("en-US", { year: "numeric", month: "long" })`.

The card body has no explicit `font-size`. It inherits the `body` element's
18px/17px/16.5px scale (`layouts/Base.astro`), the same rule article prose
runs on, so a note and an article read at the same size at every breakpoint
without a second hardcoded number to keep in sync.

The footer is pinned to the card's bottom edge with `margin-top: auto`.

The permalink must stay reachable by keyboard. `:focus-within` on the card
handles that, so tabbing to the anchor reveals it.

No handwriting font. `--font-hand` stays unused and no font dependency is added.

### Grid

```css
display: grid;
grid-template-columns: 1fr;
gap: 20px;
```

One card per row. Order is strictly newest first, top to bottom. No column
breakpoint is needed since the grid is already single-column at every width.

## Pages

### `/notes/`

Heading "Notes", then `<NoteWall notes={notes} permalinks />`. Empty state reads
"Nothing here yet.", styled the same way the Article index styles its own empty
state. The wording differs because "published" means nothing for a type with no
draft flag.

Uses the same 940px breakout as the home page's `.intro` and `.feed`, because a
three-column grid needs more than the 760px site shell.

### Home page

Order below the intro, unchanged above it:

1. `Articles` heading, existing list, max 5, "See all articles" when more exist
2. `Notes` heading, `<NoteWall>` with the newest 3, no permalinks, "See all
   notes" when more than 3 exist

`NOTE_LIMIT = 3`. Cards on the home page are plain content and link nowhere;
"See all notes" is the only call to action in that section.

The Notes section reuses the existing `.feed` breakout on the home page, the
940px `margin-left: 50%` plus `translateX(-50%)` pattern, so its left edge lines
up with the bio text and the Articles list above it. `NoteWall`'s own
`max-width: var(--reading-width)` then caps each card's line length inside
that wider block, so the Articles list can use the full breakout width while
Note text stays as narrow as article prose.

### Header

Nav becomes two links, in order: **Articles**, **Notes**. Each renders only when
its collection has entries, preserving the existing behaviour that production
never shows a dead link. Active-state logic extends to both paths.

## Seed Notes

Four, all `2026-08-02`, all displaying "August 2026". Times descend so the wall
order matches the order below.

| Slug | Time | Opening line |
| --- | --- | --- |
| `comprehension-debt` | `T12:00` | "There is something appealing about still watching tutorial videos..." |
| `sales-sustains-the-business` | `T11:00` | "When I was young in my software engineering career..." |
| `do-hard-things` | `T10:00` | "The person you are when no one is watching is the real you." |
| `discipline-on-bad-days` | `T09:00` | "Staying on track is easy when you're having a good day." |

Bodies are the user's text verbatim, with paragraph breaks preserved and stray
leading whitespace cleaned up.

## File changes

Renames use `git mv` so history follows.

| From | To |
| --- | --- |
| `src/content/posts/` | `src/content/articles/` |
| `src/pages/posts/` | `src/pages/articles/` |
| `src/utils/posts.ts` | `src/utils/articles.ts` |
| `docs/context/posts/` | `docs/context/articles/` |
| `docs/post-types.md` | `docs/article-types.md` |

New:

- `src/content/notes/` with the four seed Notes
- `src/utils/notes.ts`, exporting `getNotes()`
- `src/pages/notes/index.astro`
- `src/components/NoteWall.astro`
- `public/_redirects`

Edited:

- `src/content.config.ts`: collection key `posts` to `articles`, add `notes`
- `src/utils/articles.ts`: `getPublishedPosts` to `getPublishedArticles`
- `src/pages/articles/index.astro`: heading and meta to "Articles"
- `src/pages/articles/[...slug].astro`: back link to `/articles/`, label
  "Articles"
- `src/components/layout/Header.astro`: two nav links
- `src/pages/index.astro`: heading to "Articles", add the Notes section
- `docs/article-types.md`, `docs/writing-tips.md`: "post" reworded to "article"

Docs already written as part of this design: `CONTEXT.md`, `CONTEXT-MAP.md`,
`docs/adr/0001-single-posts-collection.md` (marked superseded),
`docs/adr/0003-notes-as-a-separate-collection.md`.

## Out of scope

- Individual Note pages
- Tag pages or filtering for either type
- A draft mechanism for Notes
- RSS
- Removing the unused `--font-hand` variable from `global.css`

## Verification

- `pnpm build` passes, which runs `astro check` and fails on type errors. The
  collection rename touches typed `CollectionEntry` references, so this is the
  real check.
- `pnpm lint` passes.
- `/articles/set-up-your-ai-coding-agent/` renders; `/posts/...` 301s to it once
  deployed.
- `/notes/` shows four cards stacked one per row, newest first
  (`comprehension-debt` on top), all reading "August 2026".
- `/notes/#comprehension-debt` scrolls to the correct card.
- Home page shows Articles then three Notes.
- Both themes render the card correctly, and the permalink appears on keyboard
  focus as well as hover.
