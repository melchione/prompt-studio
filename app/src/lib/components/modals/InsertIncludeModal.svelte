<script lang="ts">
	import Modal from './Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import { modals, showToast, leftPanel, rightPanel, appState } from '$lib/stores/editor.svelte';
	import { onMount } from 'svelte';

	interface IncludeItem {
		project: string;
		agent: string;
		lang: string;
		section: string;
		path: string;
	}

	let includes = $state<IncludeItem[]>([]);
	let selectedProject = $state('');
	let selectedAgent = $state('');
	let selectedSection = $state('');
	let preview = $state('');

	const panel = $derived(modals.insertInclude.panelId === 'left' ? leftPanel : rightPanel);

	// Filtrer par projet
	const agents = $derived(
		[...new Set(includes.filter((i) => i.project === selectedProject).map((i) => i.agent))]
	);

	// Filtrer par agent
	const sections = $derived(
		includes.filter(
			(i) => i.project === selectedProject && i.agent === selectedAgent && i.lang === panel.lang
		)
	);

	async function loadIncludes() {
		try {
			const res = await fetch('/api/includes');
			const data = await res.json();
			includes = data.includes || [];
		} catch (e) {
			console.error('Erreur chargement includes:', e);
		}
	}

	async function loadPreview() {
		if (!selectedProject || !selectedAgent || !selectedSection) {
			preview = '';
			return;
		}

		try {
			const res = await fetch(
				`/api/projects/${selectedProject}/agents/${selectedAgent}/${panel.lang}/${selectedSection}`
			);
			const data = await res.json();
			preview = data.content?.substring(0, 500) || '';
			if (data.content && data.content.length > 500) {
				preview += '\n...';
			}
		} catch (e) {
			preview = 'Erreur chargement aperçu';
		}
	}

	function insertInclude() {
		if (!selectedSection) return;

		const includePath = `${selectedAgent}/${panel.lang}/${selectedSection}`;
		const includeTag = `{% include '${includePath}' %}`;

		// Utiliser la position du curseur stockée dans modals.insertInclude
		const { cursorLine, cursorColumn } = modals.insertInclude;

		// Convertir position ligne/colonne en index dans le contenu
		const lines = panel.content.split('\n');
		let charIndex = 0;

		for (let i = 0; i < cursorLine - 1 && i < lines.length; i++) {
			charIndex += lines[i].length + 1; // +1 pour le \n
		}
		charIndex += Math.min(cursorColumn - 1, (lines[cursorLine - 1] || '').length);

		// Insérer à la position du curseur
		const newContent =
			panel.content.slice(0, charIndex) +
			'\n' + includeTag + '\n' +
			panel.content.slice(charIndex);

		// Mettre à jour content ET collapsedContent pour que collapse fonctionne
		panel.content = newContent;
		panel.collapsedContent = newContent;
		panel.isModified = true;
		panel.hasIncludes = true;

		showToast('Include inséré', 'success');
		closeModal();
	}

	function closeModal() {
		modals.insertInclude.open = false;
		modals.insertInclude.panelId = null;
		selectedProject = '';
		selectedAgent = '';
		selectedSection = '';
		preview = '';
	}

	$effect(() => {
		if (modals.insertInclude.open) {
			loadIncludes();
		}
	});

	$effect(() => {
		if (selectedSection) {
			loadPreview();
		}
	});

	$effect(() => {
		// Reset agent quand projet change
		if (selectedProject) {
			selectedAgent = '';
			selectedSection = '';
		}
	});

	$effect(() => {
		// Reset section quand agent change
		if (selectedAgent) {
			selectedSection = '';
		}
	});
</script>

<Modal open={modals.insertInclude.open} onclose={closeModal} title="Insérer un include">
	<div class="space-y-4">
		<!-- Sélection en cascade - un select par ligne -->
		<div class="flex flex-col gap-1">
			<label class="text-sm text-text-secondary">Projet</label>
			<Select
				value={selectedProject}
				onchange={(e) => (selectedProject = e.currentTarget.value)}
				placeholder="Sélectionner un projet"
			>
				{#each appState.projects as project}
					<option value={project.name}>{project.name}</option>
				{/each}
			</Select>
		</div>

		<div class="flex flex-col gap-1">
			<label class="text-sm text-text-secondary">Agent</label>
			<Select
				value={selectedAgent}
				onchange={(e) => (selectedAgent = e.currentTarget.value)}
				placeholder="Sélectionner un agent"
				disabled={!selectedProject}
			>
				{#each agents as agent}
					<option value={agent}>{agent}</option>
				{/each}
			</Select>
		</div>

		<div class="flex flex-col gap-1">
			<label class="text-sm text-text-secondary">Section</label>
			<Select
				value={selectedSection}
				onchange={(e) => (selectedSection = e.currentTarget.value)}
				placeholder="Sélectionner une section"
				disabled={!selectedAgent}
			>
				{#each sections as section}
					<option value={section.section}>{section.section}</option>
				{/each}
			</Select>
		</div>

		<!-- Aperçu -->
		{#if preview}
			<div>
				<label class="mb-1 block text-xs text-text-muted">Aperçu</label>
				<div class="max-h-32 overflow-y-auto rounded bg-bg-tertiary p-2 text-xs text-text-secondary">
					<pre class="whitespace-pre-wrap">{preview}</pre>
				</div>
			</div>
		{/if}

		<!-- Actions -->
		<div class="flex justify-end gap-2">
			<Button onclick={closeModal}>Annuler</Button>
			<Button variant="primary" onclick={insertInclude} disabled={!selectedSection}>
				Insérer
			</Button>
		</div>
	</div>
</Modal>
