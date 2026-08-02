import { type CollectionEntry, getCollection } from "astro:content";

/**
 * Published articles, newest first. Drafts are excluded in production builds and
 * kept visible in dev so work-in-progress can be previewed locally.
 */
export async function getPublishedArticles(): Promise<CollectionEntry<"articles">[]> {
	const articles = await getCollection("articles", ({ data }) =>
		import.meta.env.PROD ? !data.draft : true,
	);
	return articles.sort((a, b) => b.data.publishDate.valueOf() - a.data.publishDate.valueOf());
}
