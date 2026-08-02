# Context

Shared vocabulary and positioning for sanveerosahan.com.

## Positioning

- **Audience**: broad personal brand. Not tuned for recruiters or a single role. Anyone who lands here (peers, collaborators, future readers). Written to age well.
- **Identity spine**: building and customer value. Sanveer builds; the point of building is value customers trust and businesses run on.
- **Self-label**: "software engineer", with data engineering and the data ecosystem as the stated passion. No current-employer claim in the opener and no tenure count, so the page stays true across role changes. Past employers (Atlan, Boltic) appear inside the achievement paragraphs, not the hero.
- **Home structure**: inspired by arpitbhayani.me (Name, tagline, prose content). No side-projects section, because there are none. The Databricks-depth paragraph fills that slot. Below the intro sit two feeds: Articles, then Notes.

## Voice

- Personal-site voice, not resume voice. A human sentence over a LinkedIn summary. First person, present tense.
- No hard metrics on the Home page. Concrete achievements stated plainly ("minutes instead of hours"), numbers left in the resume. Keeps the page durable.
- Follows the global writing rules: no em-dashes, no negation frames, varied sentence length.

## Canonical terms

- **Name**: "Sanveer Singh Osahan" is the canonical full name. Use it everywhere the identity appears: hero, header wordmark, `site.config.ts` (`title` and `author`), page titles, OG, alt text. Not "Sanveer Osahan". The site name doubles as the home page's browser-tab title, so the home tab reads the bare name while subpages read "Page | Sanveer Singh Osahan".
- **Tagline**: the one identity line under the name. "I build customer value through engineering, leading teams that ship what customers trust and businesses grow on." A shortened form of the resume tagline. Reuse verbatim if referenced elsewhere.

### Writing

The site publishes two kinds of writing, and they are different types, not variants of one.

- **Article**: a titled piece of long-form writing published at `/articles/<slug>/`. Guides, explainers, opinion pieces, and video companions are all Articles. Has a title, a description, and a reading time. _Avoid_: Post, blog post, entry.
- **Note**: one idea, self-contained, read in a single breath. No title, no description, no headings, no sections. Roughly 150 words or less. Notes appear only as cards on the Notes wall at `/notes/`, never as their own page. Always Sanveer's own words. A quotation from someone else is not a Note. _Avoid_: Thought, sticky, quote, micro-post.
- **The boundary**: if a piece needs a title to make sense, or wants headings, it is an Article. This is a judgment rule that Sanveer applies while writing. Nothing in the build enforces it.
- **Draft**: an Article with `draft: true`. Visible in local dev, excluded from production builds and the sitemap. Applies to Articles only. Notes have no draft mechanism, so for a Note the folder is the publish switch: a file in `src/content/notes/` is live on the wall and in the sitemap the moment it exists. Unfinished Notes live outside that folder.
- **Video companion**: an Article that has an optional `videoUrl`. The Article is the written form; the YouTube video is the paired form. An Article can exist without a video. The video does not define the Article; it is metadata on it.
- **The wall**: the Notes page at `/notes/`. A three-column grid of cards, newest first, showing every Note in full. The home page shows the newest three from the same wall.

### Note ordering

A Note's card shows month and year, never the day. The day and time in `publishDate` exist purely to order the wall, which means several Notes published on the same day can be ordered exactly by giving them different times. Readers see only "August 2026" either way.

## Per-article contexts

Each Article carries its own context for terms and decisions local to that Article. This file holds only site-wide vocabulary. See `CONTEXT-MAP.md` for the index. Notes are too short to warrant their own contexts.
