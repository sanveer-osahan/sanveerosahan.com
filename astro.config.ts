import sitemap from "@astrojs/sitemap";
import tailwind from "@astrojs/tailwind";
import { defineConfig } from "astro/config";
import robotsTxt from "astro-robots-txt";
import webmanifest from "astro-webmanifest";
import { siteConfig } from "./src/site.config";

export default defineConfig({
	site: "https://sanveerosahan.com",
	output: "static",
	build: {
		inlineStylesheets: "always",
	},
	integrations: [
		tailwind({
			applyBaseStyles: false,
		}),
		sitemap({
			changefreq: "weekly",
			priority: 0.7,
		}),
		robotsTxt(),
		webmanifest({
			name: siteConfig.title,
			description: siteConfig.description,
			lang: siteConfig.lang,
			icon: "public/icon.png",
			icons: [
				{
					src: "icons/apple-touch-icon.png",
					sizes: "180x180",
					type: "image/png",
				},
				{
					src: "icons/icon-192.png",
					sizes: "192x192",
					type: "image/png",
				},
				{
					src: "icons/icon-512.png",
					sizes: "512x512",
					type: "image/png",
				},
			],
			start_url: "/",
			background_color: "#1d1f21",
			theme_color: "#2bbc8a",
			display: "standalone",
			config: {
				insertFaviconLinks: false,
				insertThemeColorMeta: false,
				insertManifestLink: false,
			},
		}),
		(await import("@playform/compress")).default(),
	],
	prefetch: true,
});
