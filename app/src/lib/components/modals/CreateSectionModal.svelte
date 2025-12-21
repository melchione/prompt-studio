<script lang="ts">
	import Modal from './Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { modals, showToast, leftPanel, rightPanel, persistPanel } from '$lib/stores/editor.svelte';

	let sectionName = $state('');
	let isLoading = $state(false);

	const panel = $derived(modals.createSection.panelId === 'left' ? leftPanel : rightPanel);

	async function createSection() {
		if (!sectionName.trim() || !panel.project || !panel.agent) return;

		isLoading = true;
		try {
			const res = await fetch(
				`/api/projects/${panel.project}/agents/${panel.agent}/${panel.lang}/create-section`,
				{
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ name: sectionName.trim() })
				}
			);

			const data = await res.json();
			if (data.success) {
				panel.sections = [...panel.sections, data.section];
				panel.currentSection = data.section.name;
				panel.content = `# ${sectionName.trim()}\n\n`;
				panel.originalContent = panel.content;
				panel.isModified = false;
				persistPanel(modals.createSection.panelId!);
				showToast('Section créée', 'success');
				closeModal();
			} else {
				showToast(data.error || 'Erreur', 'error');
			}
		} catch (e) {
			console.error('Erreur création section:', e);
			showToast('Erreur de création', 'error');
		} finally {
			isLoading = false;
		}
	}

	function closeModal() {
		modals.createSection.open = false;
		modals.createSection.panelId = null;
		sectionName = '';
	}
</script>

<Modal open={modals.createSection.open} onclose={closeModal} title="Nouvelle section">
	<form onsubmit={(e) => { e.preventDefault(); createSection(); }}>
		<div class="mb-4">
			<label for="section-name" class="mb-2 block text-sm text-text-secondary">
				Nom de la section
			</label>
			<input
				id="section-name"
				type="text"
				bind:value={sectionName}
				placeholder="ex: instructions, context, examples..."
				class="w-full rounded-md border border-border bg-bg-tertiary px-3 py-2 text-text-primary
					placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-blue"
				disabled={isLoading}
			/>
		</div>

		<div class="flex justify-end gap-2">
			<Button onclick={closeModal} disabled={isLoading}>
				Annuler
			</Button>
			<Button
				variant="primary"
				onclick={createSection}
				disabled={!sectionName.trim() || isLoading}
			>
				{isLoading ? 'Création...' : 'Créer'}
			</Button>
		</div>
	</form>
</Modal>
