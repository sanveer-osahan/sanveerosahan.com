const WORDS_PER_MINUTE = 200;

/**
 * Minutes to read a post body, from its raw markdown source. Strips fenced
 * code blocks, inline code, and HTML tags before counting words so table
 * markup and copy-paste commands don't inflate the estimate.
 */
export function getReadingTime(markdown: string): number {
	const text = markdown
		.replace(/```[\s\S]*?```/g, " ")
		.replace(/`[^`]*`/g, " ")
		.replace(/<[^>]+>/g, " ");
	const words = text.split(/\s+/).filter(Boolean).length;
	return Math.max(1, Math.ceil(words / WORDS_PER_MINUTE));
}
