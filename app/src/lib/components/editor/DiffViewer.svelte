<script lang="ts">
	import { onMount, onDestroy } from 'svelte';

	let { original, modified }: { original: string; modified: string } = $props();

	let container: HTMLDivElement;
	let diffEditor: any = null;
	let monaco: any = null;

	onMount(async () => {
		const monacoModule = await import('monaco-editor');
		monaco = monacoModule;

		// Configuration du thème diff
		monaco.editor.defineTheme('prompt-studio-diff', {
			base: 'vs-dark',
			inherit: true,
			rules: [],
			colors: {
				'editor.background': '#0f172a',
				'editor.foreground': '#f8fafc',
				'diffEditor.insertedTextBackground': '#22c55e20',
				'diffEditor.removedTextBackground': '#dc262620',
				'diffEditor.insertedLineBackground': '#22c55e10',
				'diffEditor.removedLineBackground': '#dc262610'
			}
		});

		diffEditor = monaco.editor.createDiffEditor(container, {
			theme: 'prompt-studio-diff',
			readOnly: true,
			renderSideBySide: true,
			automaticLayout: true,
			minimap: { enabled: false },
			scrollBeyondLastLine: false,
			wordWrap: 'on',
			fontSize: 14,
			lineHeight: 22
		});

		diffEditor.setModel({
			original: monaco.editor.createModel(original, 'markdown'),
			modified: monaco.editor.createModel(modified, 'markdown')
		});
	});

	// Mettre à jour le contenu quand les props changent
	$effect(() => {
		if (diffEditor && monaco) {
			diffEditor.setModel({
				original: monaco.editor.createModel(original, 'markdown'),
				modified: monaco.editor.createModel(modified, 'markdown')
			});
		}
	});

	onDestroy(() => {
		if (diffEditor) {
			diffEditor.dispose();
		}
	});
</script>

<div class="h-full w-full">
	<div class="mb-2 flex gap-4 px-4 pt-2 text-sm text-text-secondary">
		<span class="flex items-center gap-2">
			<span class="h-3 w-3 rounded bg-red-500/30"></span>
			Original (sauvegardé)
		</span>
		<span class="flex items-center gap-2">
			<span class="h-3 w-3 rounded bg-green-500/30"></span>
			Modifié (actuel)
		</span>
	</div>
	<div bind:this={container} class="h-[calc(100%-32px)] w-full"></div>
</div>
