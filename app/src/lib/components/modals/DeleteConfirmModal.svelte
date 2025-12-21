<script lang="ts">
	import Modal from './Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { modals, showToast, leftPanel, rightPanel, persistPanel } from '$lib/stores/editor.svelte';

	let isLoading = $state(false);

	const panel = $derived(modals.deleteConfirm.panelId === 'left' ? leftPanel : rightPanel);

	async function deleteSection() {
		if (!modals.deleteConfirm.section || !panel.project || !panel.agent) return;

		isLoading = true;
		try {
			const res = await fetch(
				`/api/projects/${panel.project}/agents/${panel.agent}/${panel.lang}/delete-section`,
				{
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ section: modals.deleteConfirm.section })
				}
			);

			const data = await res.json();
			if (data.success) {
				panel.sections = data.sections;
				if (panel.currentSection === modals.deleteConfirm.section) {
					panel.currentSection = panel.sections[0]?.name || null;
					panel.content = '';
					panel.originalContent = '';
				}
				persistPanel(modals.deleteConfirm.panelId!);
				showToast('Section supprimée', 'success');
				closeModal();
			} else {
				showToast(data.error || 'Erreur', 'error');
			}
		} catch (e) {
			console.error('Erreur suppression section:', e);
			showToast('Erreur de suppression', 'error');
		} finally {
			isLoading = false;
		}
	}

	function closeModal() {
		modals.deleteConfirm.open = false;
		modals.deleteConfirm.section = null;
		modals.deleteConfirm.panelId = null;
	}
</script>

<Modal open={modals.deleteConfirm.open} onclose={closeModal} title="Confirmer la suppression">
	<p class="mb-4 text-text-secondary">
		Êtes-vous sûr de vouloir supprimer la section
		<strong class="text-text-primary">{modals.deleteConfirm.section}</strong> ?
		Cette action est irréversible.
	</p>

	<div class="flex justify-end gap-2">
		<Button onclick={closeModal} disabled={isLoading}>
			Annuler
		</Button>
		<Button variant="danger" onclick={deleteSection} disabled={isLoading}>
			{isLoading ? 'Suppression...' : 'Supprimer'}
		</Button>
	</div>
</Modal>
