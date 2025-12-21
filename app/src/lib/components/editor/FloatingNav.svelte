<script lang="ts">
	import type { PanelState } from '$lib/types';
	import { persistPanel, showToast, modals, concatenateSections } from '$lib/stores/editor.svelte';

	let { panel, panelId, onNavigateToSection }: {
		panel: PanelState;
		panelId: 'left' | 'right';
		onNavigateToSection?: (sectionName: string) => void;
	} = $props();

	let expanded = $state(false);
	let draggedIndex = $state<number | null>(null);
	let dragOverIndex = $state<number | null>(null);

	// Naviguer vers une section (scroll dans l'éditeur)
	function goToSection(sectionName: string) {
		panel.currentSection = sectionName;
		persistPanel(panelId);

		// Appeler le callback pour scroller dans Monaco
		if (onNavigateToSection) {
			onNavigateToSection(sectionName);
		}
	}

	function handleDragStart(e: DragEvent, index: number) {
		draggedIndex = index;
		if (e.dataTransfer) {
			e.dataTransfer.effectAllowed = 'move';
			e.dataTransfer.setData('text/plain', String(index));
		}
	}

	function handleDragOver(e: DragEvent, index: number) {
		e.preventDefault();
		if (e.dataTransfer) {
			e.dataTransfer.dropEffect = 'move';
		}
		dragOverIndex = index;
	}

	function handleDragLeave() {
		dragOverIndex = null;
	}

	function handleDragEnd() {
		draggedIndex = null;
		dragOverIndex = null;
	}

	async function handleDrop(e: DragEvent, targetIndex: number) {
		e.preventDefault();

		if (draggedIndex === null || draggedIndex === targetIndex) {
			handleDragEnd();
			return;
		}

		// Réorganiser localement
		const sections = [...panel.sections];
		const [moved] = sections.splice(draggedIndex, 1);
		sections.splice(targetIndex, 0, moved);

		// Mettre à jour l'ordre des fichiers (renommer) - utiliser 'order' pas 'sections'
		const newOrder = sections.map((s) => s.name);

		try {
			const res = await fetch(
				`/api/projects/${panel.project}/agents/${panel.agent}/reorder`,
				{
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ lang: panel.lang, order: newOrder })
				}
			);

			if (res.ok) {
				// Recharger les métadonnées des sections
				const agentRes = await fetch(
					`/api/projects/${panel.project}/agents/${panel.agent}`
				);
				const agentData = await agentRes.json();
				panel.sections = agentData.sections[panel.lang] || [];

				// Recharger le contenu concaténé avec le nouvel ordre
				const allRes = await fetch(
					`/api/projects/${panel.project}/agents/${panel.agent}/${panel.lang}/all`
				);
				const allData = await allRes.json();
				if (allData.sections && allData.order) {
					const { content, boundaries } = concatenateSections(allData.sections, allData.order);
					panel.content = content;
					panel.collapsedContent = content;
					panel.originalContent = content;
					panel.sectionBoundaries = boundaries;
					panel.isModified = false;
					panel.isExpanded = false;
				}

				showToast('Sections réordonnées', 'success');
			} else {
				const errorData = await res.json();
				showToast(errorData.error || 'Erreur lors du réordonnancement', 'error');
			}
		} catch (err) {
			console.error('Erreur reorder:', err);
			showToast('Erreur lors du réordonnancement', 'error');
		}

		handleDragEnd();
	}

	function openCreateModal() {
		modals.createSection.open = true;
		modals.createSection.panelId = panelId;
	}
</script>

<nav
	class="absolute left-3 top-3 z-20"
	onmouseenter={() => (expanded = true)}
	onmouseleave={() => (expanded = false)}
>
	<div
		class="flex flex-col gap-1 overflow-hidden rounded-lg border border-border bg-bg-secondary/90 p-1 backdrop-blur-sm transition-all
			{expanded ? 'max-h-[500px] w-48' : 'max-h-[500px] w-10'}"
	>
		{#each panel.sections as section, i}
			{@const isActive = section.name === panel.currentSection}
			{@const isDragging = draggedIndex === i}
			{@const isDragOver = dragOverIndex === i && draggedIndex !== i}
			<button
				type="button"
				draggable="true"
				ondragstart={(e) => handleDragStart(e, i)}
				ondragover={(e) => handleDragOver(e, i)}
				ondragleave={handleDragLeave}
				ondragend={handleDragEnd}
				ondrop={(e) => handleDrop(e, i)}
				onclick={() => goToSection(section.name)}
				class="flex items-center gap-2 rounded px-2 py-1 text-left text-sm transition-all
					{isActive
					? 'bg-accent-blue text-white'
					: 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'}
					{isDragging ? 'opacity-50' : ''}
					{isDragOver ? 'border-t-2 border-accent-blue' : ''}"
			>
				<span
					class="flex h-6 w-6 shrink-0 cursor-grab items-center justify-center rounded-full text-xs font-bold
						{isActive ? 'bg-white/20' : 'bg-bg-tertiary'}"
				>
					{String(i + 1).padStart(2, '0')}
				</span>
				{#if expanded}
					<span class="truncate">{section.name.replace(/^\d+-/, '').replace('.md', '')}</span>
				{/if}
			</button>
		{/each}

		<!-- Bouton ajouter section -->
		<button
			type="button"
			onclick={openCreateModal}
			class="flex items-center gap-2 rounded px-2 py-1 text-left text-sm transition-colors
				text-accent-green hover:bg-bg-tertiary"
		>
			<span
				class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent-green/20 text-lg font-bold"
			>
				+
			</span>
			{#if expanded}
				<span class="truncate">Ajouter section</span>
			{/if}
		</button>
	</div>
</nav>
