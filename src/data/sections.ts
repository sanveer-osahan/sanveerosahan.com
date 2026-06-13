import type { SectionCollection } from "@/data/content";

/** Display + routing metadata for each content section. */
export interface SectionMeta {
	/** The content collection backing this section. */
	collection: SectionCollection;
	/** Short nav / eyebrow label, e.g. "Books". */
	label: string;
	/** Longer page title, e.g. "Bookshelf". */
	title: string;
	/** Root-relative base path, e.g. "/books". */
	basePath: string;
	/** Whether `/og-image/<slug>.png` cards are generated for this section. */
	hasOgImage: boolean;
}

export const SECTIONS: Record<SectionCollection, SectionMeta> = {
	post: {
		collection: "post",
		label: "Blog",
		title: "Blog",
		basePath: "/blog",
		hasOgImage: true,
	},
	book: {
		collection: "book",
		label: "Books",
		title: "Bookshelf",
		basePath: "/books",
		hasOgImage: false,
	},
	guide: {
		collection: "guide",
		label: "Guides",
		title: "How-to Guides",
		basePath: "/guides",
		hasOgImage: false,
	},
	video: {
		collection: "video",
		label: "Videos",
		title: "Videos",
		basePath: "/videos",
		hasOgImage: false,
	},
};

/** Build a section's detail URL for a slug, e.g. ("book", "atomic-habits") → "/books/atomic-habits/". */
export function sectionHref(collection: SectionCollection, slug: string): string {
	return `${SECTIONS[collection].basePath}/${slug}/`;
}

/** Map a Video `relatedTo.section` value to its backing collection. */
export function relatedSectionToCollection(
	section: "book" | "blog" | "guide",
): SectionCollection {
	return section === "blog" ? "post" : section;
}
