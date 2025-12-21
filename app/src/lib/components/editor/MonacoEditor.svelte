<script lang="ts">
	import type { PanelState } from '$lib/types';
	import { onMount, onDestroy } from 'svelte';
	import {
		persistPanel,
		triggerAutoSave,
		manualSave,
		modals,
		saveToOriginDirect,
		saveAndRebuildAll,
		leftPanel,
		rightPanel
	} from '$lib/stores/editor.svelte';

	// On reçoit panelId comme prop, mais on utilise directement le store pour la réactivité
	let { panelId }: { panelId: 'left' | 'right' } = $props();

	// Accès direct au panel depuis le store (référence directe, pas $derived)
	// panelId ne change pas pendant la vie du composant, donc c'est safe
	const panel = panelId === 'left' ? leftPanel : rightPanel;

	let container: HTMLDivElement;
	let editor = $state<any>(null);
	let monaco = $state<any>(null);
	let decorations: string[] = [];

	// Patterns pour les décorations
	const SECTION_DELIMITER_PATTERN = /<!-- ═+.*═+ -->/;
	const SECTION_NAME_PATTERN = /<!-- 📄 SECTION: (.+\.md) -->/;
	const INCLUDE_START_PATTERN = /<!-- @include-start: (.+) -->/;
	const INCLUDE_END_PATTERN = /<!-- @include-end: (.+) -->/;
	const INCLUDE_DIRECTIVE_PATTERN = /\{% include ['"](.+)['"] %\}/;

	// Appliquer les décorations
	function applyDecorations() {
		if (!editor || !monaco) return;

		const model = editor.getModel();
		if (!model) return;

		const newDecorations: any[] = [];
		const lineCount = model.getLineCount();

		for (let i = 1; i <= lineCount; i++) {
			const line = model.getLineContent(i);

			// Délimiteur de section (lignes ═══)
			if (SECTION_DELIMITER_PATTERN.test(line)) {
				newDecorations.push({
					range: new monaco.Range(i, 1, i, line.length + 1),
					options: {
						isWholeLine: true,
						className: 'section-delimiter-line',
						glyphMarginClassName: 'section-delimiter-glyph',
						overviewRuler: {
							color: '#3b82f6',
							position: monaco.editor.OverviewRulerLane.Left
						}
					}
				});
			}

			// Nom de section
			const sectionMatch = line.match(SECTION_NAME_PATTERN);
			if (sectionMatch) {
				newDecorations.push({
					range: new monaco.Range(i, 1, i, line.length + 1),
					options: {
						isWholeLine: true,
						className: 'section-name-line',
						glyphMarginClassName: 'section-name-glyph'
					}
				});
			}

			// Include directive {% include 'xxx' %}
			const includeMatch = line.match(INCLUDE_DIRECTIVE_PATTERN);
			if (includeMatch) {
				newDecorations.push({
					range: new monaco.Range(i, 1, i, line.length + 1),
					options: {
						isWholeLine: true,
						className: 'include-directive-line',
						glyphMarginClassName: 'include-glyph',
						overviewRuler: {
							color: '#22c55e',
							position: monaco.editor.OverviewRulerLane.Right
						}
					}
				});
			}

			// Include start marker
			if (INCLUDE_START_PATTERN.test(line)) {
				newDecorations.push({
					range: new monaco.Range(i, 1, i, line.length + 1),
					options: {
						isWholeLine: true,
						className: 'include-start-line'
					}
				});
			}

			// Include end marker
			if (INCLUDE_END_PATTERN.test(line)) {
				newDecorations.push({
					range: new monaco.Range(i, 1, i, line.length + 1),
					options: {
						isWholeLine: true,
						className: 'include-end-line'
					}
				});
			}
		}

		decorations = editor.deltaDecorations(decorations, newDecorations);
	}

	onMount(async () => {
		// Import dynamique pour éviter SSR issues
		const monacoModule = await import('monaco-editor');
		monaco = monacoModule;

		// Configuration du thème avec couleurs pour les décorations
		monaco.editor.defineTheme('prompt-studio-dark', {
			base: 'vs-dark',
			inherit: true,
			rules: [
				{ token: 'comment', foreground: '6A9955' },
				{ token: 'keyword', foreground: '569CD6' },
				{ token: 'string', foreground: 'CE9178' }
			],
			colors: {
				'editor.background': '#0f172a',
				'editor.foreground': '#f8fafc',
				'editorLineNumber.foreground': '#64748b',
				'editorCursor.foreground': '#3b82f6',
				'editor.selectionBackground': '#3b82f640'
			}
		});

		editor = monaco.editor.create(container, {
			value: panel.content,
			language: 'markdown',
			theme: 'prompt-studio-dark',
			wordWrap: 'on',
			minimap: { enabled: false },
			fontSize: 14,
			lineHeight: 22,
			padding: { top: 16, bottom: 16 },
			scrollBeyondLastLine: false,
			automaticLayout: true,
			tabSize: 2,
			folding: true,
			lineNumbers: 'on',
			renderWhitespace: 'none',
			quickSuggestions: false,
			glyphMargin: true
		});

		// Écouter les changements
		editor.onDidChangeModelContent(() => {
			const newContent = editor.getValue();
			console.log('[Monaco] Content changed, newContent length:', newContent.length, 'panel.content length:', panel.content.length);
			if (newContent !== panel.content) {
				panel.content = newContent;

				// Comparer avec le bon original selon le mode (expanded ou non)
				const referenceContent = panel.isExpanded
					? panel.originalExpandedContent
					: panel.originalContent;
				console.log('[Monaco] isExpanded:', panel.isExpanded, 'referenceContent length:', referenceContent?.length, 'content length:', panel.content.length);
				console.log('[Monaco] Are they equal?', panel.content === referenceContent);
				panel.isModified = panel.content !== referenceContent;
				console.log('[Monaco] isModified set to:', panel.isModified);

				persistPanel(panelId);

				// Auto-save si modifié
				if (panel.isModified) {
					triggerAutoSave(panelId);
				}

				// Mettre à jour les décorations
				applyDecorations();
			}
		});

		// Raccourci Ctrl+S pour sauvegarde manuelle
		editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
			manualSave(panelId);
		});

		// Raccourci Ctrl+Shift+S pour sauvegarde directe dans l'origine (sans popup)
		editor.addCommand(
			monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyS,
			() => {
				saveToOriginDirect(panelId);
			}
		);

		// Raccourci Ctrl+Alt+S pour sauvegarde origine + rebuild tous les dépendants
		editor.addCommand(
			monaco.KeyMod.CtrlCmd | monaco.KeyMod.Alt | monaco.KeyCode.KeyS,
			() => {
				saveAndRebuildAll(panelId);
			}
		);

		// Action pour insérer un include (clic droit + Ctrl+I)
		editor.addAction({
			id: 'insert-include',
			label: 'Insérer un include',
			keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyI],
			contextMenuGroupId: 'navigation',
			contextMenuOrder: 1.5,
			run: () => {
				// Sauvegarder la position du curseur
				const position = editor.getPosition();
				modals.insertInclude = {
					open: true,
					panelId,
					cursorLine: position?.lineNumber || 1,
					cursorColumn: position?.column || 1
				};
			}
		});

		// Appliquer les décorations initiales
		applyDecorations();
	});

	// Sync content quand panel.content change depuis l'extérieur
	$effect(() => {
		// Lire panel.content AVANT le check de editor pour garantir le tracking
		const content = panel.content;
		if (editor && content !== editor.getValue()) {
			const position = editor.getPosition();
			editor.setValue(content);
			if (position) {
				editor.setPosition(position);
			}
			// Ré-appliquer les décorations après mise à jour du contenu
			applyDecorations();
		}
	});

	// Note: On permet maintenant l'édition des includes expandés
	// Le système de sauvegarde gère la détection des modifications

	// Fonction pour naviguer vers une section
	export function goToSection(sectionName: string) {
		if (!editor || !panel.sectionBoundaries) return;

		const boundary = panel.sectionBoundaries.find((b) => b.section === sectionName);
		if (boundary) {
			editor.revealLineInCenter(boundary.startLine);
			editor.setPosition({ lineNumber: boundary.startLine, column: 1 });
			editor.focus();
		}
	}

	onDestroy(() => {
		// Annuler l'auto-save timer si présent
		if (panel.autoSaveTimer) {
			clearTimeout(panel.autoSaveTimer);
		}
		if (editor) {
			editor.dispose();
		}
	});
</script>

<div bind:this={container} class="h-full w-full"></div>
