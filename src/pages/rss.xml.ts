import { type SectionCollection, getSection, getSortDate } from "@/data/content";
import { sectionHref } from "@/data/sections";
import { siteConfig } from "@/site-config";
import { absoluteUrl } from "@/utils/path";
import rss from "@astrojs/rss";

const SECTION_COLLECTIONS: SectionCollection[] = ["post", "book", "guide", "video"];

export const GET = async () => {
	// One combined feed across every content type. Drafts are excluded by getSection in prod.
	const tagged = (
		await Promise.all(
			SECTION_COLLECTIONS.map(async (collection) => {
				const entries = await getSection(collection);
				return entries.map((entry) => ({ entry, collection }));
			}),
		)
	).flat();

	tagged.sort((a, b) => getSortDate(b.entry).valueOf() - getSortDate(a.entry).valueOf());

	return rss({
		title: siteConfig.title,
		description: siteConfig.description,
		site: absoluteUrl("/", import.meta.env.SITE),
		items: tagged.map(({ entry, collection }) => ({
			title: entry.data.title,
			description: entry.data.description,
			pubDate: entry.data.publishDate,
			link: absoluteUrl(sectionHref(collection, entry.id), import.meta.env.SITE),
		})),
	});
};
