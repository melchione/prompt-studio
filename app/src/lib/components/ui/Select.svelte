<script lang="ts">
	let {
		value = '',
		onchange,
		placeholder = 'Sélectionner...',
		disabled = false,
		children
	}: {
		value?: string;
		onchange?: (e: Event & { currentTarget: HTMLSelectElement }) => void;
		placeholder?: string;
		disabled?: boolean;
		children?: any;
	} = $props();
</script>

<select
	{value}
	{onchange}
	{disabled}
	class="min-w-[120px] rounded-md border border-border bg-bg-tertiary px-3 py-1.5 text-sm
		text-text-primary transition-colors
		hover:bg-border focus:outline-none focus:ring-2 focus:ring-accent-blue
		disabled:cursor-not-allowed disabled:opacity-50"
>
	{#if !value}
		<option value="" disabled>{placeholder}</option>
	{/if}
	{@render children?.()}
</select>
