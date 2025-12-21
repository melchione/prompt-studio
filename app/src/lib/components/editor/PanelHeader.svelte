<script lang="ts">
	import type { PanelState } from '$lib/types';
	import {
		appState,
		persistPanel,
		showToast,
		setLoading,
		concatenateSections,
		parseSectionsFromContent
	} from '$lib/stores/editor.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import LanguageToggle from '$lib/components/ui/LanguageToggle.svelte';
	import AgentBrowser from './AgentBrowser.svelte';
	import { FolderOpen, ChevronDown } from 'lucide-svelte';

	let { panel, panelId }: { panel: PanelState; panelId: 'left' | 'right' } = $props();

	let agents = $state<{ name: string }[]>([]);
	let browserOpen = $state(false);

	// Handler pour sélection depuis le browser
	async function handleAgentSelect(project: string, agent: string) {
		browserOpen = false;

		if (project !== panel.project) {
			await onProjectChange(project);
		}
		await onAgentChange(agent);
	}

	// Charger les agents quand le projet change
	async function loadAgents(project: string) {
		if (!project) {
			agents = [];
			return;
		}
		try {
			const res = await fetch(`/api/projects/${project}/agents`);
			const data = await res.json();
			agents = data.agents || [];
		} catch (e) {
			console.error('Erreur chargement agents:', e);
			agents = [];
		}
	}

	// Charger TOUTES les sections concaténées
	async function loadAllSections(project: string, agent: string, lang: string) {
		if (!project || !agent) {
			panel.sections = [];
			panel.content = '';
			return;
		}
		try {
			// Charger les métadonnées des sections
			const agentRes = await fetch(`/api/projects/${project}/agents/${agent}`);
			const agentData = await agentRes.json();
			panel.sections = agentData.sections?.[lang] || [];

			// Charger le contenu de toutes les sections
			const allRes = await fetch(`/api/projects/${project}/agents/${agent}/${lang}/all`);
			const allData = await allRes.json();

			if (allData.sections && allData.order) {
				// Concaténer avec délimiteurs
				const { content, boundaries } = concatenateSections(allData.sections, allData.order);
				panel.content = content;
				panel.collapsedContent = content;
				panel.originalContent = content;
				panel.sectionBoundaries = boundaries;
				panel.currentSection = allData.order[0] || null;
				panel.isModified = false;

				// Vérifier s'il y a des includes à expandre
				panel.hasIncludes = content.includes("{% include");

				// Expandre les includes automatiquement
				if (panel.hasIncludes) {
					await expandIncludes();
				}
			}

			persistPanel(panelId);
		} catch (e) {
			console.error('Erreur chargement sections:', e);
			panel.sections = [];
		}
	}

	// Expandre les includes
	async function expandIncludes() {
		if (!panel.project) return;

		try {
			const res = await fetch('/api/expand', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					project: panel.project,
					lang: panel.lang,
					content: panel.content
				})
			});

			if (res.ok) {
				const data = await res.json();
				if (data.error) {
					console.error('Erreur expand:', data.error);
					showToast('Erreur lors de l\'expansion des includes', 'error');
					return;
				}
				panel.content = data.content || panel.content;
				panel.isExpanded = true;
			} else {
				showToast('Erreur lors de l\'expansion des includes', 'error');
			}
		} catch (e) {
			console.error('Erreur expand:', e);
			showToast('Erreur lors de l\'expansion des includes', 'error');
		}
	}

	// Collapse les includes (revenir au contenu original)
	function collapseIncludes() {
		panel.content = panel.collapsedContent;
		panel.isExpanded = false;
	}

	// Toggle expand/collapse
	async function toggleExpand() {
		if (panel.isExpanded) {
			collapseIncludes();
		} else {
			await expandIncludes();
		}
	}

	// Handlers de changement
	async function onProjectChange(project: string) {
		panel.project = project;
		panel.agent = null;
		panel.currentSection = null;
		panel.content = '';
		panel.sections = [];
		panel.sectionBoundaries = [];
		await loadAgents(project);
		persistPanel(panelId);
	}

	async function onAgentChange(agent: string) {
		panel.agent = agent;
		panel.currentSection = null;
		panel.content = '';
		panel.sectionBoundaries = [];
		await loadAllSections(panel.project!, agent, panel.lang);
		persistPanel(panelId);
	}

	async function onLangChange(lang: 'fr' | 'en') {
		panel.lang = lang;
		if (panel.project && panel.agent) {
			await loadAllSections(panel.project, panel.agent, lang);
		}
		persistPanel(panelId);
	}

	// Sauvegarder toutes les sections
	async function save() {
		if (!panel.project || !panel.agent) return;

		setLoading(true, 'Sauvegarde...');
		try {
			// Parser le contenu pour extraire les sections individuelles
			const sectionsData = parseSectionsFromContent(panel.content);

			// Sauvegarder chaque section
			const savePromises = Object.entries(sectionsData).map(([sectionName, content]) =>
				fetch(
					`/api/projects/${panel.project}/agents/${panel.agent}/${panel.lang}/${sectionName}`,
					{
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify({ content })
					}
				)
			);

			const results = await Promise.all(savePromises);
			const allOk = results.every((r) => r.ok);

			if (allOk) {
				panel.originalContent = panel.content;
				panel.collapsedContent = panel.content;
				panel.isModified = false;
				showToast(`${Object.keys(sectionsData).length} sections sauvegardées`, 'success');

				// Auto-build
				await fetch('/api/build', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ project: panel.project, export: true })
				});
			} else {
				showToast('Erreur de sauvegarde', 'error');
			}
		} catch (e) {
			console.error('Erreur sauvegarde:', e);
			showToast('Erreur de sauvegarde', 'error');
		} finally {
			setLoading(false);
		}
	}

	// Toggle view mode
	function togglePreview() {
		panel.viewMode = panel.viewMode === 'preview' ? 'editor' : 'preview';
	}

	function toggleDiff() {
		panel.viewMode = panel.viewMode === 'diff' ? 'editor' : 'diff';
	}

	// Init au montage
	$effect(() => {
		if (panel.project) {
			loadAgents(panel.project);
			if (panel.agent) {
				loadAllSections(panel.project, panel.agent, panel.lang);
			}
		}
	});
</script>

<div
	class="flex flex-wrap items-center gap-2 border-b border-border bg-bg-secondary p-3"
>
	<!-- Bouton navigateur projet/agent -->
	<button
		onclick={() => (browserOpen = !browserOpen)}
		class="flex items-center gap-2 rounded-md bg-bg-tertiary px-3 py-1.5 text-sm
			text-text-primary transition-colors hover:bg-border"
	>
		<FolderOpen size={16} />
		{#if panel.project && panel.agent}
			<span class="font-medium">{panel.project}</span>
			<span class="text-text-muted">/</span>
			<span>{panel.agent}</span>
		{:else}
			<span class="text-text-muted">Sélectionner un agent...</span>
		{/if}
		<ChevronDown size={14} class="transition-transform {browserOpen ? 'rotate-180' : ''}" />
	</button>

	<!-- Toggle langue -->
	<LanguageToggle value={panel.lang} onchange={onLangChange} />

	<!-- Spacer -->
	<div class="flex-1"></div>

	<!-- Indicateur modification -->
	{#if panel.isModified}
		<div class="h-2 w-2 rounded-full bg-accent-yellow" title="Modifications non sauvegardées"></div>
	{/if}

	<!-- Boutons actions -->
	<Button onclick={save} variant="primary" disabled={!panel.isModified}>
		Save
	</Button>

	{#if panel.hasIncludes}
		<Button onclick={toggleExpand} active={panel.isExpanded} variant={panel.isExpanded ? 'success' : 'default'}>
			{panel.isExpanded ? 'Collapse' : 'Expand'}
		</Button>
	{/if}

	<Button onclick={togglePreview} active={panel.viewMode === 'preview'}>
		Preview
	</Button>

	<Button onclick={toggleDiff} active={panel.viewMode === 'diff'}>
		Diff
	</Button>
</div>

<!-- Panneau navigateur dépliable -->
<AgentBrowser
	bind:isOpen={browserOpen}
	selectedProject={panel.project}
	selectedAgent={panel.agent}
	onSelect={handleAgentSelect}
	onClose={() => (browserOpen = false)}
/>
