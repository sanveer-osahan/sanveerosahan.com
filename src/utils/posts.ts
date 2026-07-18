import { type CollectionEntry, getCollection } from "astro:content";

/**
 * Published posts, newest first. Drafts are excluded in production builds and
 * kept visible in dev so work-in-progress can be previewed locally.
 */
export async function getPublishedPosts(): Promise<CollectionEntry<"posts">[]> {
	const posts = await getCollection("posts", ({ data }) =>
		import.meta.env.PROD ? !data.draft : true,
	);
	return posts.sort((a, b) => b.data.publishDate.valueOf() - a.data.publishDate.valueOf());
}
