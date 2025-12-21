<script lang="ts">
	import { appState } from '$lib/stores/editor.svelte';
</script>

{#if appState.isLoading}
	<div class="fixed inset-0 z-[2000] flex items-center justify-center bg-black/70">
		<div class="flex flex-col items-center gap-4">
			<div
				class="h-10 w-10 animate-spin rounded-full border-[3px] border-bg-tertiary border-t-accent-blue"
			></div>
			{#if appState.loadingText}
				<p class="text-sm text-text-secondary">{appState.loadingText}</p>
			{/if}
		</div>
	</div>
{/if}
