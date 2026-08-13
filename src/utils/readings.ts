import { type CollectionEntry, getCollection } from "astro:content";

/**
 * Published Readings, newest first by `readDate`. Drafts are excluded in
 * production builds and kept visible in dev, which matches Articles: a Reading
 * needs somewhere to sit while the book details get checked.
 */
export async function getReadings(): Promise<CollectionEntry<"bookshelf">[]> {
	const readings = await getCollection("bookshelf", ({ data }) =>
		import.meta.env.PROD ? !data.draft : true,
	);
	return readings.sort((a, b) => b.data.readDate.valueOf() - a.data.readDate.valueOf());
}
