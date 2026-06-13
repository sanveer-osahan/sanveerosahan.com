import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

function removeDupsAndLowerCase(array: string[]) {
	if (!array.length) return array;
	const lowercaseItems = array.map((str) => str.toLowerCase());
	const distinctItems = new Set(lowercaseItems);
	return Array.from(distinctItems);
}

const post = defineCollection({
	loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/post" }),
	schema: ({ image }) =>
		z.object({
			coverImage: z
				.object({
					alt: z.string(),
					src: image(),
				})
				.optional(),
			description: z.string().min(10).max(160),
			draft: z.boolean().default(false),
			ogImage: z.string().optional(),
			publishDate: z
				.string()
				.or(z.date())
				.transform((val) => new Date(val)),
			tags: z.array(z.string()).default([]).transform(removeDupsAndLowerCase),
			title: z.string().max(120),
			updatedDate: z
				.string()
				.optional()
				.transform((str) => (str ? new Date(str) : undefined)),
		}),
});

// Book Notes — Sanveer's takeaways from a book he's read, carrying the book's
// metadata. Amazon links are plain URLs now but stored in a dedicated field so an
// affiliate tag + disclosure can be layered on later without a schema change (ADR-0001).
const book = defineCollection({
	loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/book" }),
	schema: ({ image }) =>
		z.object({
			title: z.string().max(120),
			author: z.string(),
			amazonUrl: z.string().url(),
			coverImage: z
				.object({
					alt: z.string(),
					src: image(),
				})
				.optional(),
			description: z.string().min(10).max(160),
			draft: z.boolean().default(false),
			ogImage: z.string().optional(),
			publishDate: z
				.string()
				.or(z.date())
				.transform((val) => new Date(val)),
			tags: z.array(z.string()).default([]).transform(removeDupsAndLowerCase),
			updatedDate: z
				.string()
				.optional()
				.transform((str) => (str ? new Date(str) : undefined)),
		}),
});

// How-to Guides — task-oriented walkthroughs. Same core as a blog post plus optional
// procedural fields.
const guide = defineCollection({
	loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/guide" }),
	schema: z.object({
		title: z.string().max(120),
		description: z.string().min(10).max(160),
		draft: z.boolean().default(false),
		ogImage: z.string().optional(),
		prerequisites: z.array(z.string()).default([]),
		estimatedTime: z.string().optional(),
		publishDate: z
			.string()
			.or(z.date())
			.transform((val) => new Date(val)),
		tags: z.array(z.string()).default([]).transform(removeDupsAndLowerCase),
		updatedDate: z
			.string()
			.optional()
			.transform((str) => (str ? new Date(str) : undefined)),
	}),
});

// Videos — a YouTube video, carrying its link and the published raw prep content (the
// body) used to make it. `relatedTo` optionally points at the piece it was derived from;
// it crosses collection boundaries, hence the {section, slug} shape rather than a
// single-collection reference (ADR-0001).
const video = defineCollection({
	loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/video" }),
	schema: z.object({
		title: z.string().max(120),
		description: z.string().min(10).max(160),
		youtubeUrl: z.string().url(),
		relatedTo: z
			.object({
				section: z.enum(["book", "blog", "guide"]),
				slug: z.string(),
			})
			.optional(),
		draft: z.boolean().default(false),
		ogImage: z.string().optional(),
		publishDate: z
			.string()
			.or(z.date())
			.transform((val) => new Date(val)),
		tags: z.array(z.string()).default([]).transform(removeDupsAndLowerCase),
		updatedDate: z
			.string()
			.optional()
			.transform((str) => (str ? new Date(str) : undefined)),
	}),
});

const page = defineCollection({
	loader: glob({ pattern: "**/*.md", base: "./src/content/page" }),
	schema: z.object({
		title: z.string().max(120),
		description: z.string().max(160).optional(),
	}),
});

export const collections = { post, book, guide, video, page };
