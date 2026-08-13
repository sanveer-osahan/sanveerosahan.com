import { glob } from "astro/loaders";
import { defineCollection, z } from "astro:content";

const articles = defineCollection({
	loader: glob({ base: "./src/content/articles", pattern: "**/*.md" }),
	schema: z.object({
		title: z.string(),
		description: z.string(),
		publishDate: z.coerce.date(),
		draft: z.boolean().default(false),
		tags: z.array(z.string()).default([]),
		videoUrl: z.string().url().optional(),
	}),
});

/*
 * A Note is the whole body: no title, no description, nothing to stage.
 * There is deliberately no `draft` flag, so any file in this folder is live.
 * `publishDate` carries a time because cards render month and year only,
 * which makes the time free ordering control for same-day notes.
 */
const notes = defineCollection({
	loader: glob({ base: "./src/content/notes", pattern: "**/*.md" }),
	schema: z.object({
		publishDate: z.coerce.date(),
	}),
});

/*
 * A Reading is one book plus what Sanveer took from it. The frontmatter is the
 * book: facts about the world that never change. The body is the reading: it
 * starts empty and grows chapter by chapter, so an entry goes live long before
 * it is finished.
 *
 * `readDate` never renders. It exists to order the shelf, the same way a Note's
 * time of day orders the wall. Sorting on `publishedDate` instead would pin a
 * classic below a new release forever, which says nothing about when he read it.
 */
const bookshelf = defineCollection({
	loader: glob({ base: "./src/content/bookshelf", pattern: "**/*.md" }),
	schema: ({ image }) =>
		z.object({
			title: z.string(),
			subtitle: z.string().optional(),
			author: z.array(z.string()),
			publishedDate: z.coerce.date(),
			publisher: z.string(),
			pages: z.number(),
			cover: image(),
			readDate: z.coerce.date(),
			amazonCom: z.string().url().optional(),
			amazonIn: z.string().url().optional(),
			draft: z.boolean().default(false),
		}),
});

export const collections = { articles, notes, bookshelf };
