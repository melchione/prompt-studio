<script lang="ts">
	let {
		open = false,
		onclose,
		title,
		children
	}: {
		open: boolean;
		onclose?: () => void;
		title?: string;
		children?: any;
	} = $props();

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			onclose?.();
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			onclose?.();
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
	<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
		onclick={handleBackdropClick}
	>
		<div
			class="w-full max-w-md rounded-xl border border-border bg-bg-secondary p-6 shadow-2xl"
			role="dialog"
			aria-modal="true"
		>
			{#if title}
				<h2 class="mb-4 text-lg font-semibold text-text-primary">{title}</h2>
			{/if}
			{@render children?.()}
		</div>
	</div>
{/if}
