export interface SiteConfig {
	/** Site-wide display name. */
	author: string;
	description: string;
	lang: string;
	ogLocale: string;
	title: string;
	hideThemeCredit?: boolean;
}

export interface SiteMeta {
	articleDate?: string | undefined;
	description?: string;
	ogImage?: string | undefined;
	/**
	 * Real pixel size of `ogImage`. The default social card is 1200x630, so a
	 * page that supplies its own image must state its size or the tags lie.
	 * A portrait image also switches the Twitter card to the small variant,
	 * because the large one crops anything that is taller than it is wide.
	 */
	ogImageWidth?: number;
	ogImageHeight?: number;
	title: string;
}
