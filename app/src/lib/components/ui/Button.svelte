<script lang="ts">
	type Variant = 'default' | 'primary' | 'success' | 'danger' | 'warning';

	let {
		onclick,
		variant = 'default',
		disabled = false,
		active = false,
		children
	}: {
		onclick?: () => void;
		variant?: Variant;
		disabled?: boolean;
		active?: boolean;
		children?: any;
	} = $props();

	const variantClasses: Record<Variant, string> = {
		default: 'bg-bg-tertiary border-border hover:bg-border',
		primary: 'bg-accent-blue border-accent-blue hover:bg-blue-600 text-white',
		success: 'bg-accent-green border-accent-green hover:bg-green-600 text-white',
		danger: 'bg-accent-red border-accent-red hover:bg-red-700 text-white',
		warning: 'bg-accent-yellow border-accent-yellow hover:bg-yellow-500 text-black'
	};
</script>

<button
	type="button"
	{onclick}
	{disabled}
	class="rounded-md border px-3 py-1.5 text-sm font-medium transition-colors
		{variantClasses[variant]}
		{active ? 'ring-2 ring-accent-blue ring-offset-1 ring-offset-bg-primary' : ''}
		{disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}"
>
	{@render children?.()}
</button>
