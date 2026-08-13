# Context

Shared vocabulary and positioning for sanveerosahan.com.

## Positioning

- **Audience**: broad personal brand. Not tuned for recruiters or a single role. Anyone who lands here (peers, collaborators, future readers). Written to age well.
- **Identity spine**: building and customer value. Sanveer builds; the point of building is value customers trust and businesses run on.
- **Self-label**: "software engineer", with data engineering and the data ecosystem as the stated passion. No current-employer claim in the opener and no tenure count, so the page stays true across role changes. Past employers (Atlan, Boltic) appear inside the achievement paragraphs, not the hero.
- **Home structure**: inspired by arpitbhayani.me (Name, tagline, prose content). No side-projects section, because there are none. The Databricks-depth paragraph fills that slot. Below the intro sit three sections: Articles, then Notes, then the Bookshelf row.

## Voice

- Personal-site voice, not resume voice. A human sentence over a LinkedIn summary. First person, present tense.
- No hard metrics on the Home page. Concrete achievements stated plainly ("minutes instead of hours"), numbers left in the resume. Keeps the page durable.
- Follows the global writing rules: no em-dashes, no negation frames, varied sentence length.

## Canonical terms

- **Name**: "Sanveer Singh Osahan" is the canonical full name. Use it everywhere the identity appears: hero, header wordmark, `site.config.ts` (`title` and `author`), page titles, OG, alt text. Not "Sanveer Osahan". The site name doubles as the home page's browser-tab title, so the home tab reads the bare name while subpages read "Page | Sanveer Singh Osahan".
- **Tagline**: the one identity line under the name. "I build customer value through engineering, leading teams that ship what customers trust and businesses grow on." A shortened form of the resume tagline. Reuse verbatim if referenced elsewhere.

### Writing

The site publishes three kinds of writing, and they are different types, not variants of one.

- **Article**: a titled piece of long-form writing published at `/articles/<slug>/`. Guides, explainers, opinion pieces, and video companions are all Articles. Has a title, a description, and a reading time. _Avoid_: Post, blog post, entry.
- **Reading**: one book, plus what Sanveer took from it. Published at `/bookshelf/<slug>/`. The book metadata is a fact about the world and never changes. The learnings are his, and they grow chapter by chapter, so a Reading goes live long before it is finished. Written as chapter headings with paragraphs under them. _Avoid_: Book review, book note, summary. A Reading is not a summary of the book; it is what he understood from it.
- **Book**: the metadata block inside a Reading. Title, subtitle, authors, publisher, publication date, page count, cover, and the buy links. A Book never appears on its own. Use this word only for the facts, never for the page.
- **Note**: one idea, self-contained, read in a single breath. No title, no description, no headings, no sections. Roughly 150 words or less. Notes appear only as cards on the Notes wall at `/notes/`, never as their own page. Always Sanveer's own words. A quotation from someone else is not a Note. _Avoid_: Thought, sticky, quote, micro-post.
- **The boundary**: if a piece needs a title to make sense, or wants headings, it is an Article. This is a judgment rule that Sanveer applies while writing. Nothing in the build enforces it. A Reading sits outside this boundary: it is defined by having a Book attached, not by its length or its shape.
- **Draft**: an Article or a Reading with `draft: true`. Visible in local dev, excluded from production builds and the sitemap. Notes have no draft mechanism, so for a Note the folder is the publish switch: a file in `src/content/notes/` is live on the wall and in the sitemap the moment it exists. Unfinished Notes live outside that folder.
- **Reading in progress**: a Reading with an empty body. The page shows the Book and one italic line saying the learnings are still to come. A Reading carries no status field, so this is the only way the site says a book is unfinished. Once the first chapter is written, the line is gone for good.
- **Video companion**: an Article that has an optional `videoUrl`. The Article is the written form; the YouTube video is the paired form. An Article can exist without a video. The video does not define the Article; it is metadata on it.
- **The wall**: the Notes page at `/notes/`. A single column of cards, newest first, showing every Note in full. The home page shows the newest three from the same wall.
- **The shelf**: the Bookshelf page at `/bookshelf/`. A single-column list, newest first. Each row is a cover thumbnail and the title, with the authors under it. The home page is the exception: it shows the newest three as a row of full covers under the heading "From my bookshelf".

### Note ordering

A Note's card shows month and year, never the day. The day and time in `publishDate` exist purely to order the wall, which means several Notes published on the same day can be ordered exactly by giving them different times. Readers see only "August 2026" either way.

### Reading ordering

A Reading carries two dates and they mean different things. `publishedDate` is when the book was published, and it renders on the page. `readDate` is when Sanveer read it, it orders the shelf, and it never renders anywhere. Sorting on `publishedDate` instead would pin a classic below a new release forever, which says nothing about his reading.

### Bookshelf heading

The home section reads "From my bookshelf", not "Books I've read recently". A Reading carries no status, so the site cannot tell a finished book from one opened yesterday. A tense-neutral heading stays true in both cases without a field to maintain.

## Per-article contexts

Each Article carries its own context for terms and decisions local to that Article. This file holds only site-wide vocabulary. See `CONTEXT-MAP.md` for the index. Notes are too short to warrant their own contexts, and a Reading takes its framing from the book it covers.
