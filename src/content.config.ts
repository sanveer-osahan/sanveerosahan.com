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

export const collections = { articles, notes };
