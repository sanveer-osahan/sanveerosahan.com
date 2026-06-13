import { type CollectionEntry, getCollection } from "astro:content";
import { siteConfig } from "@/site-config";

/** Collections that behave as dated, listable content sections. */
export type SectionCollection = "post" | "book" | "guide" | "video";

/** Anything sortable by publish/updated date — the shared shape across sections. */
type Dated = { data: { publishDate: Date; updatedDate?: Date } };

/** Fetch a section's entries. Drafts are excluded in production builds. */
export async function getSection<C extends SectionCollection>(
	collection: C,
): Promise<CollectionEntry<C>[]> {
	return await getCollection(collection, ({ data }) =>
		import.meta.env.PROD ? !data.draft : true,
	);
}

/** Date used for sorting — `updatedDate` if `siteConfig.sortPostsByUpdatedDate`, else `publishDate`. */
export function getSortDate(entry: Dated): Date {
	return siteConfig.sortPostsByUpdatedDate && entry.data.updatedDate !== undefined
		? new Date(entry.data.updatedDate)
		: new Date(entry.data.publishDate);
}

/** Sort by `getSortDate`, newest first. Returns a new array. */
export function sortByDate<T extends Dated>(entries: T[]): T[] {
	return [...entries].sort((a, b) => getSortDate(b).valueOf() - getSortDate(a).valueOf());
}
