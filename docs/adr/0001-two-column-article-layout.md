# 1. Two-column layout for Articles and Readings

Date: 2026-08-28

## Status

Accepted

## Context

An Article and a Reading needed on-page navigation built from their headings,
pinned to the right of the prose while the reader scrolls.

Every page on the site renders inside `.wrap` in `src/layouts/Base.astro`, which
is `max-width: 760px` and centred. That 760px is the reading measure: the line
length the serif body type was set for. There was nowhere to put a second column
without changing something.

Three options:

1. Widen `.wrap` on the Article and Reading templates only, then lay the two
   columns out in a grid inside it.
2. Leave `.wrap` at 760px and position the Contents absolutely in the right
   margin.
3. Widen `.wrap` for every page.

## Decision

Option 1. `Base.astro` takes a `wide` prop that raises `max-width` to 1120px.
Only the two article-shaped templates pass it. Inside, a grid splits the shell
into `minmax(0, 760px)` for the prose and 240px for the Contents.

**The prose column is a fixed 760px, not a fraction of the wider shell.** Line
length is identical to what it was before. The block simply stops being centred
and sits left of centre, with the Contents in the space that opens on the right.

Below 1120px the two columns no longer fit. The shell drops back to 760px, the
Contents column is hidden, and the page is byte-for-byte the layout that shipped
before this change.

## Consequences

- Home, Notes, the Bookshelf index, About, and 404 are untouched. They keep the
  760px shell and stay centred.
- An Article is off-centre on a wide screen even when it has no Contents to show
  (fewer than two headings, or a Reading in progress). The column is still drawn,
  empty. Letting the page recentre itself would move the prose sideways depending
  on how many chapters a Reading happened to have, which reads as a bug.
- Option 2 was rejected because a Contents outside the grid has no relationship
  to the content width. It would collide with the prose below roughly 1200px and
  drift far from it on a wide monitor.
- Option 3 was rejected because it changes the measure on every page to solve a
  problem that exists on two.
