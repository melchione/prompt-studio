<script lang="ts">
	import { appState } from '$lib/stores/editor.svelte';

	interface ProjectWithAgents {
		name: string;
		agents: string[];
	}

	let {
		isOpen = $bindable(false),
		selectedProject,
		selectedAgent,
		onSelect,
		onClose
	}: {
		isOpen: boolean;
		selectedProject: string | null;
		selectedAgent: string | null;
		onSelect: (project: string, agent: string) => void;
		onClose: () => void;
	} = $props();

	let projectsWithAgents = $state<ProjectWithAgents[]>([]);
	let loading = $state(false);

	// Charger les agents quand le browser s'ouvre
	$effect(() => {
		if (isOpen && projectsWithAgents.length === 0) {
			loadAllAgents();
		}
	});

	async function loadAllAgents() {
		loading = true;
		try {
			const results = await Promise.all(
				appState.projects.map(async (project) => {
					const res = await fetch(`/api/projects/${project.name}/agents`);
					const data = await res.json();
					return {
						name: project.name,
						agents: data.agents?.map((a: { name: string }) => a.name) || []
					};
				})
			);
			projectsWithAgents = results;
		} catch (e) {
			console.error('Erreur chargement agents:', e);
		} finally {
			loading = false;
		}
	}
</script>

{#if isOpen}
	<!-- Overlay pour click outside -->
	<div
		class="fixed inset-0 z-10"
		onclick={onClose}
		onkeydown={(e) => e.key === 'Escape' && onClose()}
		role="button"
		tabindex="-1"
	></div>

	<!-- Browser panel -->
	<div class="relative z-20 border-b border-border bg-bg-secondary p-4">
		{#if loading}
			<div class="flex items-center gap-2 text-sm text-text-muted">
				<svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24">
					<circle
						class="opacity-25"
						cx="12"
						cy="12"
						r="10"
						stroke="currentColor"
						stroke-width="4"
						fill="none"
					></circle>
					<path
						class="opacity-75"
						fill="currentColor"
						d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
					></path>
				</svg>
				Chargement des agents...
			</div>
		{:else}
			<div class="flex gap-6 overflow-x-auto">
				{#each projectsWithAgents as project}
					<div class="min-w-[160px] flex-shrink-0">
						<!-- Nom du projet -->
						<div
							class="mb-2 flex items-center gap-2 border-b border-border pb-1 text-sm font-semibold text-text-primary"
						>
							<span class="text-accent-blue">📁</span>
							{project.name}
						</div>
						<!-- Liste des agents -->
						<div class="max-h-[250px] space-y-1 overflow-y-auto">
							{#each project.agents as agent}
								<button
									onclick={() => onSelect(project.name, agent)}
									class="w-full rounded px-2 py-1.5 text-left text-sm transition-colors
                    {selectedProject === project.name && selectedAgent === agent
										? 'bg-accent-blue text-white'
										: 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'}"
								>
									{agent}
								</button>
							{/each}
							{#if project.agents.length === 0}
								<span class="px-2 text-xs italic text-text-muted">Aucun agent</span>
							{/if}
						</div>
					</div>
				{/each}
				{#if projectsWithAgents.length === 0}
					<div class="text-sm text-text-muted">Aucun projet trouvé</div>
				{/if}
			</div>
		{/if}
	</div>
{/if}
