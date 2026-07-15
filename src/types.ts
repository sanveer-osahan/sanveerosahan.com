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
	title: string;
}
