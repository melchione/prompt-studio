<script lang="ts">
	import { FileEdit, Copy, RefreshCw, ChevronRight, Loader2 } from 'lucide-svelte';
	import Modal from './Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import {
		modals,
		showToast,
		leftPanel,
		rightPanel,
		closeSaveIncludeModal,
		saveIncludesToOrigin,
		buildAgent,
		copyIncludesToLocal,
		fetchDependents,
		setLoading
	} from '$lib/stores/editor.svelte';

	let isLoading = $state(false);
	let loadingDependents = $state(false);

	const panel = $derived(modals.saveInclude.panelId === 'left' ? leftPanel : rightPanel);
	const hasMultipleIncludes = $derived(modals.saveInclude.modifiedIncludes.length > 1);

	// Phase 1: Choose action (origin vs local)
	async function chooseOrigin() {
		modals.saveInclude.selectedAction = 'origin';

		// Fetch dependents for phase 2
		if (panel.project) {
			loadingDependents = true;
			try {
				const deps = await fetchDependents(panel.project, modals.saveInclude.modifiedIncludes);
				modals.saveInclude.dependents = deps;
			} catch (e) {
				console.error('Error fetching dependents:', e);
			} finally {
				loadingDependents = false;
			}
		}

		// Move to phase 2
		modals.saveInclude.phase = 2;
	}

	async function chooseLocal() {
		modals.saveInclude.selectedAction = 'local';
		isLoading = true;

		try {
			const success = await copyIncludesToLocal(modals.saveInclude.panelId!);
			if (success) {
				closeSaveIncludeModal();
			}
		} catch (e) {
			console.error('Error copying to local:', e);
			showToast('Erreur lors de la copie locale', 'error');
		} finally {
			isLoading = false;
		}
	}

	// Phase 2: Choose build scope
	async function saveAndBuild() {
		isLoading = true;

		try {
			setLoading(true, 'Sauvegarde des fichiers sources...');

			const saved = await saveIncludesToOrigin(modals.saveInclude.panelId!);
			if (!saved) {
				showToast('Erreur lors de la sauvegarde', 'error');
				return;
			}

			if (modals.saveInclude.buildScope === 'current') {
				// Build only current file
				setLoading(true, 'Build du fichier actuel...');
				await buildAgent(modals.saveInclude.panelId!);
				showToast('Sauvegardé et buildé', 'success');
			} else {
				// Build all dependents
				setLoading(true, 'Build de tous les fichiers dépendants...');
				await buildAgent(modals.saveInclude.panelId!);

				// Also rebuild all dependent files
				if (modals.saveInclude.dependents.length > 0) {
					await fetch('/api/build', {
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify({ project: panel.project, export: true })
					});
				}

				const count = modals.saveInclude.dependents.length + 1;
				showToast(`${count} fichier(s) rebuildé(s)`, 'success');
			}

			closeSaveIncludeModal();
		} catch (e) {
			console.error('Error during save and build:', e);
			showToast('Erreur lors de la sauvegarde', 'error');
		} finally {
			isLoading = false;
			setLoading(false);
		}
	}

	function goBackToPhase1() {
		modals.saveInclude.phase = 1;
		modals.saveInclude.selectedAction = null;
		modals.saveInclude.dependents = [];
	}
</script>

<Modal
	open={modals.saveInclude.open}
	onclose={closeSaveIncludeModal}
	title={modals.saveInclude.phase === 1
		? 'Sauvegarde des Includes Modifiés'
		: 'Options de Build'}
>
	{#if modals.saveInclude.phase === 1}
		<!-- Phase 1: Choose origin vs local -->
		<div class="space-y-4">
			<p class="text-sm text-text-secondary">
				Vous avez modifié le contenu inclus depuis :
			</p>

			<ul class="space-y-1 rounded-lg border border-border bg-bg-tertiary p-3">
				{#each modals.saveInclude.modifiedIncludes as inc}
					<li class="flex items-center gap-2 text-sm text-text-primary">
						<FileEdit class="h-4 w-4 text-accent-blue" />
						<code class="rounded bg-bg-primary px-1">{inc.path}</code>
					</li>
				{/each}
			</ul>

			<p class="text-sm text-text-secondary">
				Comment souhaitez-vous sauvegarder ?
			</p>

			<div class="space-y-2">
				<!-- Option: Save to origin -->
				<button
					class="flex w-full items-start gap-3 rounded-lg border border-border bg-bg-tertiary p-4 text-left transition-colors hover:bg-border"
					onclick={chooseOrigin}
					disabled={isLoading || loadingDependents}
				>
					<div class="mt-0.5 rounded-lg bg-accent-blue/20 p-2">
						<FileEdit class="h-5 w-5 text-accent-blue" />
					</div>
					<div class="flex-1">
						<div class="font-medium text-text-primary">Modifier le fichier d'origine</div>
						<div class="text-sm text-text-secondary">
							{#if hasMultipleIncludes}
								Enregistre les modifications dans les {modals.saveInclude.modifiedIncludes.length} fichiers sources
							{:else}
								Enregistre dans <code class="rounded bg-bg-primary px-1">{modals.saveInclude.modifiedIncludes[0]?.path}</code>
							{/if}
						</div>
					</div>
					<ChevronRight class="mt-2 h-5 w-5 text-text-tertiary" />
				</button>

				<!-- Option: Copy locally -->
				<button
					class="flex w-full items-start gap-3 rounded-lg border border-border bg-bg-tertiary p-4 text-left transition-colors hover:bg-border"
					onclick={chooseLocal}
					disabled={isLoading || loadingDependents}
				>
					<div class="mt-0.5 rounded-lg bg-accent-green/20 p-2">
						<Copy class="h-5 w-5 text-accent-green" />
					</div>
					<div class="flex-1">
						<div class="font-medium text-text-primary">Copier ici (supprimer l'include)</div>
						<div class="text-sm text-text-secondary">
							Le contenu remplace les directives <code class="rounded bg-bg-primary px-1">{`{% include %}`}</code>
						</div>
					</div>
					{#if isLoading}
						<Loader2 class="mt-2 h-5 w-5 animate-spin text-text-tertiary" />
					{/if}
				</button>
			</div>

			<div class="flex justify-end pt-2">
				<Button onclick={closeSaveIncludeModal} disabled={isLoading}>
					Annuler
				</Button>
			</div>
		</div>
	{:else}
		<!-- Phase 2: Choose build scope -->
		<div class="space-y-4">
			{#if loadingDependents}
				<div class="flex items-center gap-2 text-sm text-text-secondary">
					<Loader2 class="h-4 w-4 animate-spin" />
					Recherche des fichiers dépendants...
				</div>
			{:else if modals.saveInclude.dependents.length > 0}
				<p class="text-sm text-text-secondary">
					Fichiers qui incluent {hasMultipleIncludes ? 'ces fichiers' : 'ce fichier'} :
				</p>

				<ul class="max-h-32 space-y-1 overflow-y-auto rounded-lg border border-border bg-bg-tertiary p-3">
					{#each modals.saveInclude.dependents as dep}
						<li class="text-sm text-text-primary">
							<code class="rounded bg-bg-primary px-1">{dep.agent}</code>
							<span class="text-text-tertiary">({dep.lang})</span>
						</li>
					{/each}
				</ul>
			{:else}
				<p class="text-sm text-text-secondary">
					Aucun autre fichier n'inclut {hasMultipleIncludes ? 'ces fichiers' : 'ce fichier'}.
				</p>
			{/if}

			<p class="text-sm text-text-secondary">
				Que souhaitez-vous rebuilder ?
			</p>

			<div class="space-y-2">
				<label class="flex cursor-pointer items-center gap-3 rounded-lg border border-border bg-bg-tertiary p-3 transition-colors hover:bg-border">
					<input
						type="radio"
						name="buildScope"
						value="current"
						bind:group={modals.saveInclude.buildScope}
						class="h-4 w-4 text-accent-blue"
					/>
					<span class="text-sm text-text-primary">Seulement le fichier actuel</span>
				</label>

				<label
					class="flex cursor-pointer items-center gap-3 rounded-lg border border-border bg-bg-tertiary p-3 transition-colors hover:bg-border
					{modals.saveInclude.dependents.length === 0 ? 'opacity-50' : ''}"
				>
					<input
						type="radio"
						name="buildScope"
						value="all"
						bind:group={modals.saveInclude.buildScope}
						disabled={modals.saveInclude.dependents.length === 0}
						class="h-4 w-4 text-accent-blue"
					/>
					<span class="text-sm text-text-primary">
						Tous les fichiers dépendants
						{#if modals.saveInclude.dependents.length > 0}
							<span class="text-text-tertiary">({modals.saveInclude.dependents.length + 1} fichiers)</span>
						{/if}
					</span>
				</label>
			</div>

			<div class="flex justify-between pt-2">
				<Button onclick={goBackToPhase1} disabled={isLoading}>
					Retour
				</Button>
				<div class="flex gap-2">
					<Button onclick={closeSaveIncludeModal} disabled={isLoading}>
						Annuler
					</Button>
					<Button variant="primary" onclick={saveAndBuild} disabled={isLoading}>
						{#if isLoading}
							<span class="flex items-center gap-2">
								<Loader2 class="h-4 w-4 animate-spin" />
								Sauvegarde...
							</span>
						{:else}
							<span class="flex items-center gap-2">
								<RefreshCw class="h-4 w-4" />
								Sauvegarder et Builder
							</span>
						{/if}
					</Button>
				</div>
			</div>
		</div>
	{/if}
</Modal>
