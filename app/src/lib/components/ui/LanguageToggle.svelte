<script lang="ts">
	let {
		value = 'fr',
		onchange
	}: {
		value: 'fr' | 'en';
		onchange?: (lang: 'fr' | 'en') => void;
	} = $props();
</script>

<div class="flex overflow-hidden rounded-md border border-border">
	<button
		type="button"
		onclick={() => onchange?.('fr')}
		class="px-3 py-1.5 text-sm font-medium transition-colors
			{value === 'fr'
			? 'bg-accent-blue text-white'
			: 'bg-bg-tertiary text-text-secondary hover:bg-border'}"
	>
		FR
	</button>
	<button
		type="button"
		onclick={() => onchange?.('en')}
		class="px-3 py-1.5 text-sm font-medium transition-colors
			{value === 'en'
			? 'bg-accent-blue text-white'
			: 'bg-bg-tertiary text-text-secondary hover:bg-border'}"
	>
		EN
	</button>
</div>
