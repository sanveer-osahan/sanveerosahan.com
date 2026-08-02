import { type CollectionEntry, getCollection } from "astro:content";

/**
 * Every note, newest first. Notes have no draft flag, so the folder is the
 * publish switch: a file in src/content/notes/ is live in dev and production
 * alike. Sorting uses the full timestamp, which is how same-day notes get a
 * deliberate order without showing a day to the reader.
 */
export async function getNotes(): Promise<CollectionEntry<"notes">[]> {
	const notes = await getCollection("notes");
	return notes.sort((a, b) => b.data.publishDate.valueOf() - a.data.publishDate.valueOf());
}
