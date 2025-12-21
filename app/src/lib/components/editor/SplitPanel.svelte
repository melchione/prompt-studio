<script lang="ts">
	import type { PanelState } from '$lib/types';
	import PanelHeader from './PanelHeader.svelte';
	import FloatingNav from './FloatingNav.svelte';
	import MonacoEditor from './MonacoEditor.svelte';
	import MarkdownPreview from './MarkdownPreview.svelte';
	import DiffViewer from './DiffViewer.svelte';

	let { panel, panelId }: { panel: PanelState; panelId: 'left' | 'right' } = $props();

	let monacoEditor = $state<MonacoEditor | null>(null);

	// Callback pour naviguer vers une section dans l'éditeur
	function handleNavigateToSection(sectionName: string) {
		if (monacoEditor && panel.viewMode === 'editor') {
			monacoEditor.goToSection(sectionName);
		}
	}
</script>

<div class="flex h-full flex-col">
	<!-- Header avec sélecteurs -->
	<PanelHeader {panelId} />

	<!-- Contenu principal -->
	<div class="relative flex-1 overflow-hidden">
		<!-- Navigation flottante -->
		{#if panel.sections.length > 0}
			<FloatingNav {panel} {panelId} onNavigateToSection={handleNavigateToSection} />
		{/if}

		<!-- Éditeur ou Preview ou Diff -->
		{#if panel.viewMode === 'editor'}
			<MonacoEditor bind:this={monacoEditor} {panelId} />
		{:else if panel.viewMode === 'preview'}
			<MarkdownPreview content={panel.content} />
		{:else if panel.viewMode === 'diff'}
			<DiffViewer original={panel.originalContent} modified={panel.content} />
		{/if}
	</div>
</div>
