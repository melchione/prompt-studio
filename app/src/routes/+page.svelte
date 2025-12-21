<script lang="ts">
	import { onMount } from 'svelte';
	import { appState, showToast, setLoading } from '$lib/stores/editor.svelte';
	import SplitContainer from '$lib/components/editor/SplitContainer.svelte';
	import CreateSectionModal from '$lib/components/modals/CreateSectionModal.svelte';
	import DeleteConfirmModal from '$lib/components/modals/DeleteConfirmModal.svelte';
	import InsertIncludeModal from '$lib/components/modals/InsertIncludeModal.svelte';
	import SaveIncludeModal from '$lib/components/modals/SaveIncludeModal.svelte';

	onMount(async () => {
		setLoading(true, 'Chargement des projets...');
		try {
			const res = await fetch('/api/projects');
			const data = await res.json();
			appState.projects = data.projects || [];
			showToast('Projets chargés', 'success');
		} catch (e) {
			console.error('Erreur chargement projets:', e);
			showToast('Erreur de chargement', 'error');
		} finally {
			setLoading(false);
		}
	});
</script>

<svelte:head>
	<title>Prompt Studio</title>
</svelte:head>

<SplitContainer />

<!-- Modales -->
<CreateSectionModal />
<DeleteConfirmModal />
<InsertIncludeModal />
<SaveIncludeModal />
