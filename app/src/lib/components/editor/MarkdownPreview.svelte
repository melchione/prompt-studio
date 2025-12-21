<script lang="ts">
	import { onMount } from 'svelte';

	let { content = '' }: { content: string } = $props();

	let htmlContent = $state('');
	let md: any = null;

	onMount(async () => {
		const MarkdownIt = (await import('markdown-it')).default;
		md = new MarkdownIt({
			html: true,
			linkify: true,
			typographer: true
		});
		updateHtml();
	});

	function updateHtml() {
		if (md && content) {
			htmlContent = md.render(content);
		} else {
			htmlContent = '';
		}
	}

	$effect(() => {
		if (md) {
			updateHtml();
		}
	});
</script>

<div class="h-full overflow-y-auto bg-[#0a0a0a] p-6">
	<article class="prose prose-invert prose-sm max-w-none">
		{@html htmlContent}
	</article>
</div>

<style>
	:global(.prose h1) {
		margin-bottom: 1rem;
		border-bottom: 1px solid var(--color-border);
		padding-bottom: 0.5rem;
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-text-primary);
	}
	:global(.prose h2) {
		margin-bottom: 0.75rem;
		margin-top: 1.5rem;
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--color-text-primary);
	}
	:global(.prose h3) {
		margin-bottom: 0.5rem;
		margin-top: 1rem;
		font-size: 1.125rem;
		font-weight: 500;
		color: var(--color-text-primary);
	}
	:global(.prose p) {
		margin-bottom: 0.75rem;
		line-height: 1.625;
		color: var(--color-text-secondary);
	}
	:global(.prose code) {
		border-radius: 0.25rem;
		background-color: var(--color-bg-tertiary);
		padding: 0.125rem 0.375rem;
		color: var(--color-accent-green);
	}
	:global(.prose pre) {
		margin: 1rem 0;
		overflow-x: auto;
		border-radius: 0.5rem;
		background-color: var(--color-bg-secondary);
		padding: 1rem;
	}
	:global(.prose pre code) {
		background-color: transparent;
		padding: 0;
	}
	:global(.prose ul) {
		margin-bottom: 0.75rem;
		list-style-type: disc;
		padding-left: 1.5rem;
		color: var(--color-text-secondary);
	}
	:global(.prose ol) {
		margin-bottom: 0.75rem;
		list-style-type: decimal;
		padding-left: 1.5rem;
		color: var(--color-text-secondary);
	}
	:global(.prose li) {
		margin-bottom: 0.25rem;
	}
	:global(.prose a) {
		color: var(--color-accent-blue);
	}
	:global(.prose a:hover) {
		text-decoration: underline;
	}
	:global(.prose blockquote) {
		margin: 1rem 0;
		border-left: 4px solid var(--color-accent-blue);
		padding-left: 1rem;
		font-style: italic;
		color: var(--color-text-muted);
	}
	:global(.prose table) {
		margin: 1rem 0;
		width: 100%;
		border-collapse: collapse;
	}
	:global(.prose th),
	:global(.prose td) {
		border: 1px solid var(--color-border);
		padding: 0.5rem 0.75rem;
		text-align: left;
	}
	:global(.prose th) {
		background-color: var(--color-bg-tertiary);
		font-weight: 600;
	}
</style>
