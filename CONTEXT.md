# Context

Shared vocabulary and positioning for sanveerosahan.com.

## Positioning

- **Audience**: broad personal brand. Not tuned for recruiters or a single role. Anyone who lands here (peers, collaborators, future readers). Written to age well.
- **Identity spine**: building and customer value. Sanveer builds; the point of building is value customers trust and businesses run on.
- **Self-label**: "software engineer", with data engineering and the data ecosystem as the stated passion. No current-employer claim in the opener and no tenure count, so the page stays true across role changes. Past employers (Atlan, Boltic) appear inside the achievement paragraphs, not the hero.
- **Home structure**: inspired by arpitbhayani.me (Name, tagline, prose content). No side-projects section, because there are none. The Databricks-depth paragraph fills that slot.

## Voice

- Personal-site voice, not resume voice. A human sentence over a LinkedIn summary. First person, present tense.
- No hard metrics on the Home page. Concrete achievements stated plainly ("minutes instead of hours"), numbers left in the resume. Keeps the page durable.
- Follows the global writing rules: no em-dashes, no negation frames, varied sentence length.

## Canonical terms

- **Name**: "Sanveer Singh Osahan" is the canonical full name. Use it everywhere the identity appears: hero, header wordmark, `site.config.ts` (`title` and `author`), page titles, OG, alt text. Not "Sanveer Osahan". The site name doubles as the home page's browser-tab title, so the home tab reads the bare name while subpages read "Page | Sanveer Singh Osahan".
- **Tagline**: the one identity line under the name. "I build customer value through engineering, leading teams that ship what customers trust and businesses grow on." A shortened form of the resume tagline. Reuse verbatim if referenced elsewhere.
- **Post**: a single piece of writing published under `/posts/<slug>`. The one content type on the site. Deliberately broad. Guides, notes, and video companions are all Posts, not separate types, until the volume of one kind justifies splitting it out.
- **Draft**: a Post with `draft: true`. Visible in local dev, excluded from production builds and the sitemap. The mechanism for staging a Post publicly-invisible until it's ready. Flip to `false` to publish.
- **Video companion**: a Post that has an optional `videoUrl`. The Post is the written form; the YouTube video is the paired form. A Post can exist without a video. The video does not define the Post; it's metadata on it.
