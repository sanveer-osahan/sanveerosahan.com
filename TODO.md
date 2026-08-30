# TODO

## The mobile experience

The site is built and checked at desktop widths. Everything below has a
breakpoint that keeps it readable on a phone, but none of it is designed for
one. Treat this as a single piece of work covering every page: Home, Articles,
an Article, Notes, the Bookshelf, a Reading, About, and 404.

Known items, and the workarounds they will replace:

- **The Contents.** An Article and a Reading show their headings in a right-hand
  column above 1120px. Below that the column is hidden and the prose goes full
  width, which is exactly the layout the site had before. A phone needs its own
  treatment: a collapsed list above the article, or a bar that expands. Stacking
  the current list is not it. One Article has 16 entries, which would push the
  first paragraph off the screen.
- **The Reading's Book block.** Cover and facts sit side by side down to 480px,
  then stack. Checked, not designed.
- **Tables and code blocks** inside an Article scroll sideways in their own box.
  That stops the page from scrolling sideways. It does not make a wide table
  readable on a phone.
- **The tabsets** in "Set Up your AI Coding Agent" wrap their labels onto several
  rows at narrow widths.
