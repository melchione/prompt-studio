<script lang="ts">
	import { toasts } from '$lib/stores/editor.svelte';
</script>

<div class="fixed bottom-5 right-5 z-[2000] flex flex-col gap-2">
	{#each toasts as toast (toast.id)}
		<div
			class="animate-slide-in rounded-md border border-border bg-bg-secondary px-4 py-3 text-sm text-text-primary shadow-lg"
			class:border-l-accent-green={toast.type === 'success'}
			class:border-l-accent-red={toast.type === 'error'}
			class:border-l-accent-yellow={toast.type === 'warning'}
			style="border-left-width: 4px;"
		>
			{toast.message}
		</div>
	{/each}
</div>
