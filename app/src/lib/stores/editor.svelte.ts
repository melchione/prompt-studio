import type { Project, Agent, Section, Toast, PanelState, SectionBoundary } from '$lib/types';

// Délimiteurs de section
const SECTION_DELIMITER_START = '<!-- ══════════════════════════════════════════════════════════════════════════ -->';
const SECTION_DELIMITER_PATTERN = /<!-- 📄 SECTION: (.+\.md) -->/;

// Créer un délimiteur de section
export function createSectionDelimiter(sectionName: string): string {
	return `${SECTION_DELIMITER_START}\n<!-- 📄 SECTION: ${sectionName} -->\n${SECTION_DELIMITER_START}`;
}

// Concaténer les sections avec délimiteurs
export function concatenateSections(
	sectionsData: Record<string, string>,
	order: string[]
): { content: string; boundaries: SectionBoundary[] } {
	const parts: string[] = [];
	const boundaries: SectionBoundary[] = [];
	let currentLine = 1;

	order.forEach((sectionName) => {
		const content = sectionsData[sectionName] || '';

		// Ajouter délimiteur
		const delimiter = createSectionDelimiter(sectionName);
		parts.push(delimiter);

		const delimiterLines = delimiter.split('\n').length;
		const delimiterLine = currentLine;
		const startLine = currentLine + delimiterLines;

		// Ajouter contenu
		parts.push(content);

		const contentLines = content.split('\n').length;
		const endLine = startLine + contentLines - 1;

		boundaries.push({
			section: sectionName,
			delimiterLine,
			startLine,
			endLine
		});

		currentLine = endLine + 2; // +1 pour nouvelle ligne entre sections
		parts.push(''); // Ligne vide entre sections
	});

	return {
		content: parts.join('\n'),
		boundaries
	};
}

// Parser le contenu pour extraire les sections
export function parseSectionsFromContent(content: string): Record<string, string> {
	const sections: Record<string, string> = {};
	const lines = content.split('\n');
	let currentSection: string | null = null;
	let currentContent: string[] = [];

	for (const line of lines) {
		const match = line.match(SECTION_DELIMITER_PATTERN);
		if (match) {
			// Sauvegarder section précédente
			if (currentSection) {
				sections[currentSection] = currentContent.join('\n').trim();
			}
			currentSection = match[1];
			currentContent = [];
		} else if (currentSection && !line.startsWith('<!-- ═')) {
			currentContent.push(line);
		}
	}

	// Sauvegarder dernière section
	if (currentSection) {
		sections[currentSection] = currentContent.join('\n').trim();
	}

	return sections;
}

// État global de l'application
export const appState = $state({
	projects: [] as Project[],
	isLoading: false,
	loadingText: ''
});

// Toasts
export const toasts = $state<Toast[]>([]);

export function showToast(message: string, type: 'success' | 'error' | 'warning' = 'success') {
	const id = Date.now();
	toasts.push({ id, message, type });
	setTimeout(() => {
		const idx = toasts.findIndex((t) => t.id === id);
		if (idx !== -1) toasts.splice(idx, 1);
	}, 3000);
}

// Fonction pour créer l'état d'un panneau
function createPanelState(id: 'left' | 'right'): PanelState {
	// Côté serveur, pas de localStorage
	if (typeof window === 'undefined') {
		return {
			project: null,
			agent: null,
			lang: 'fr',
			sections: [],
			currentSection: null,
			content: '',
			originalContent: '',
			collapsedContent: '',
			originalExpandedContent: '',
			sectionBoundaries: [],
			hasIncludes: false,
			isModified: false,
			isExpanded: false,
			viewMode: 'editor',
			autoSaveTimer: null,
			lastSaved: null
		};
	}

	// Côté client, restaurer depuis localStorage
	const saved = localStorage.getItem(`panel_${id}`);
	const initial = saved ? JSON.parse(saved) : {};

	return {
		project: initial.project || null,
		agent: initial.agent || null,
		lang: initial.lang || 'fr',
		sections: [],
		currentSection: initial.currentSection || null,
		content: '',
		originalContent: '',
		collapsedContent: '',
		originalExpandedContent: '',
		sectionBoundaries: [],
		hasIncludes: false,
		isModified: false,
		isExpanded: false,
		viewMode: 'editor',
		autoSaveTimer: null,
		lastSaved: null
	};
}

// États des panneaux
export const leftPanel = $state<PanelState>(createPanelState('left'));
export const rightPanel = $state<PanelState>(createPanelState('right'));

// Types pour la modal saveInclude
export interface ModifiedInclude {
	path: string;
	originalContent: string;
	modifiedContent: string;
}

export interface IncludeDependent {
	project: string;
	agent: string;
	lang: string;
	section: string;
}

// Modales
export const modals = $state({
	createSection: { open: false, panelId: null as 'left' | 'right' | null },
	deleteConfirm: { open: false, section: null as string | null, panelId: null as 'left' | 'right' | null },
	insertInclude: { open: false, panelId: null as 'left' | 'right' | null, cursorLine: 1, cursorColumn: 1 },
	translate: { open: false, panelId: null as 'left' | 'right' | null },
	saveInclude: {
		open: false,
		panelId: null as 'left' | 'right' | null,
		phase: 1 as 1 | 2, // 1: Choose origin vs local, 2: Choose build scope
		modifiedIncludes: [] as ModifiedInclude[],
		dependents: [] as IncludeDependent[],
		selectedAction: null as 'origin' | 'local' | null,
		buildScope: 'current' as 'current' | 'all'
	}
});

// Helper pour obtenir le panneau par ID
export function getPanel(id: 'left' | 'right'): PanelState {
	return id === 'left' ? leftPanel : rightPanel;
}

// Sauvegarder dans localStorage
export function persistPanel(id: 'left' | 'right') {
	if (typeof window === 'undefined') return;

	const panel = getPanel(id);
	localStorage.setItem(
		`panel_${id}`,
		JSON.stringify({
			project: panel.project,
			agent: panel.agent,
			lang: panel.lang,
			currentSection: panel.currentSection
		})
	);
}

// Loading helpers
export function setLoading(loading: boolean, text = '') {
	appState.isLoading = loading;
	appState.loadingText = text;
}

// Auto-save delay (1.5 seconds)
const AUTOSAVE_DELAY = 1500;

// Sauvegarder une section
export async function saveSection(panelId: 'left' | 'right'): Promise<boolean> {
	const panel = getPanel(panelId);

	if (!panel.project || !panel.agent || !panel.currentSection) {
		return false;
	}

	try {
		const res = await fetch(
			`/api/projects/${panel.project}/agents/${panel.agent}/${panel.lang}/${panel.currentSection}`,
			{
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ content: panel.content })
			}
		);

		if (res.ok) {
			panel.originalContent = panel.content;
			panel.isModified = false;
			panel.lastSaved = new Date();
			return true;
		}
		return false;
	} catch (e) {
		console.error('Erreur sauvegarde:', e);
		return false;
	}
}

// Build après sauvegarde
export async function buildAgent(panelId: 'left' | 'right'): Promise<boolean> {
	const panel = getPanel(panelId);

	if (!panel.project || !panel.agent) {
		return false;
	}

	try {
		const res = await fetch('/api/build', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ project: panel.project, export: true })
		});

		return res.ok;
	} catch (e) {
		console.error('Erreur build:', e);
		return false;
	}
}

// Auto-save avec timer
export function triggerAutoSave(panelId: 'left' | 'right') {
	const panel = getPanel(panelId);

	// Annuler le timer précédent
	if (panel.autoSaveTimer) {
		clearTimeout(panel.autoSaveTimer);
	}

	// Démarrer un nouveau timer
	panel.autoSaveTimer = setTimeout(async () => {
		if (panel.isModified) {
			const saved = await saveSection(panelId);
			if (saved) {
				await buildAgent(panelId);
				showToast('Sauvegardé automatiquement', 'success');
			}
		}
	}, AUTOSAVE_DELAY);
}

// Sauvegarde manuelle (Ctrl+S)
export async function manualSave(panelId: 'left' | 'right') {
	const panel = getPanel(panelId);

	// Annuler l'auto-save en cours
	if (panel.autoSaveTimer) {
		clearTimeout(panel.autoSaveTimer);
		panel.autoSaveTimer = null;
	}

	if (!panel.isModified) {
		showToast('Aucune modification à sauvegarder', 'warning');
		return;
	}

	setLoading(true, 'Sauvegarde...');

	const saved = await saveSection(panelId);
	if (saved) {
		setLoading(true, 'Build...');
		await buildAgent(panelId);
		showToast('Sauvegardé et buildé', 'success');
	} else {
		showToast('Erreur lors de la sauvegarde', 'error');
	}

	setLoading(false);
}

// ============================================================================
// Gestion des includes modifiés
// ============================================================================

/**
 * Parse le contenu pour extraire les blocs include et leur contenu
 */
export function parseIncludeBlocks(content: string): Map<string, string> {
	const blocks = new Map<string, string>();
	const pattern = /<!-- @include-start: ([^>]+) -->\n([\s\S]*?)\n<!-- @include-end: \1 -->/g;

	let match;
	while ((match = pattern.exec(content)) !== null) {
		blocks.set(match[1], match[2]);
	}

	return blocks;
}

/**
 * Détecte les includes modifiés en comparant le contenu actuel avec le contenu original expandé
 * stocké lors du premier chargement.
 */
export function detectModifiedIncludes(panelId: 'left' | 'right'): ModifiedInclude[] {
	const panel = getPanel(panelId);

	// Vérifier que nous sommes en mode expanded et avons un original
	if (!panel.isExpanded || !panel.originalExpandedContent) {
		return [];
	}

	// Parser les blocs include actuels dans l'éditeur
	const currentBlocks = parseIncludeBlocks(panel.content);

	if (currentBlocks.size === 0) {
		return [];
	}

	// Parser les blocs include depuis le contenu original (stocké lors du premier expand)
	const originalBlocks = parseIncludeBlocks(panel.originalExpandedContent);

	const modified: ModifiedInclude[] = [];

	for (const [path, currentContent] of currentBlocks) {
		const originalContent = originalBlocks.get(path);

		// Si le contenu a changé, l'include est modifié
		if (originalContent !== undefined && originalContent !== currentContent) {
			modified.push({
				path,
				originalContent,
				modifiedContent: currentContent
			});
		}
	}

	return modified;
}

/**
 * Ouvre la modal saveInclude avec les includes modifiés
 */
export function openSaveIncludeModal(panelId: 'left' | 'right', modifiedIncludes: ModifiedInclude[]) {
	modals.saveInclude = {
		open: true,
		panelId,
		phase: 1,
		modifiedIncludes,
		dependents: [],
		selectedAction: null,
		buildScope: 'current'
	};
}

/**
 * Ferme et réinitialise la modal saveInclude
 */
export function closeSaveIncludeModal() {
	modals.saveInclude = {
		open: false,
		panelId: null,
		phase: 1,
		modifiedIncludes: [],
		dependents: [],
		selectedAction: null,
		buildScope: 'current'
	};
}

/**
 * Récupère les fichiers qui dépendent des includes modifiés
 */
export async function fetchDependents(project: string, modifiedIncludes: ModifiedInclude[]): Promise<IncludeDependent[]> {
	const allDependents: IncludeDependent[] = [];
	const seen = new Set<string>();

	for (const inc of modifiedIncludes) {
		try {
			const res = await fetch('/api/reverse-includes', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					project,
					targetFile: inc.path
				})
			});

			if (res.ok) {
				const data = await res.json();
				for (const dep of data.dependents || []) {
					const key = `${dep.agent}/${dep.lang}/${dep.section}`;
					if (!seen.has(key)) {
						seen.add(key);
						allDependents.push({
							project: dep.project,
							agent: dep.agent,
							lang: dep.lang,
							section: dep.section
						});
					}
				}
			}
		} catch (e) {
			console.error('Error fetching dependents:', e);
		}
	}

	return allDependents;
}

/**
 * Sauvegarde les includes modifiés dans leurs fichiers d'origine
 */
export async function saveIncludesToOrigin(panelId: 'left' | 'right'): Promise<boolean> {
	const panel = getPanel(panelId);

	if (!panel.project || !panel.agent || !panel.currentSection) {
		return false;
	}

	const modifiedIncludes = detectModifiedIncludes(panelId);

	if (modifiedIncludes.length === 0) {
		// Pas d'includes modifiés, sauvegarde normale
		return saveSection(panelId);
	}

	try {
		setLoading(true, 'Sauvegarde des fichiers sources...');

		// Sauvegarder chaque include modifié dans son fichier d'origine
		for (const inc of modifiedIncludes) {
			// Le path est au format 'agent/section.md' ou 'agent/lang/section.md'
			const parts = inc.path.split('/');
			let targetAgent: string;
			let targetLang: string;
			let targetSection: string;

			if (parts.length === 2) {
				// agent/section.md - utiliser la langue courante
				targetAgent = parts[0];
				targetLang = panel.lang;
				targetSection = parts[1];
			} else if (parts.length === 3) {
				// agent/lang/section.md
				targetAgent = parts[0];
				targetLang = parts[1];
				targetSection = parts[2];
			} else {
				console.error('Invalid include path:', inc.path);
				continue;
			}

			// Sauvegarder le fichier d'origine
			const res = await fetch(
				`/api/projects/${panel.project}/agents/${targetAgent}/${targetLang}/${targetSection}`,
				{
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ content: inc.modifiedContent })
				}
			);

			if (!res.ok) {
				console.error('Failed to save include:', inc.path);
				showToast(`Erreur sauvegarde ${inc.path}`, 'error');
				return false;
			}
		}

		// Maintenant sauvegarder le fichier principal (avec les marqueurs collapse)
		// On doit "collapse" le contenu pour restaurer les {% include %}
		const collapseRes = await fetch('/api/collapse', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				project: panel.project,
				lang: panel.lang,
				content: panel.content
			})
		});

		if (collapseRes.ok) {
			const collapseData = await collapseRes.json();
			// Sauvegarder le contenu collapsé
			const saveRes = await fetch(
				`/api/projects/${panel.project}/agents/${panel.agent}/${panel.lang}/${panel.currentSection}`,
				{
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ content: collapseData.content })
				}
			);

			if (saveRes.ok) {
				panel.collapsedContent = collapseData.content;
				panel.originalContent = panel.content;
				panel.isModified = false;
				panel.lastSaved = new Date();
				return true;
			}
		}

		return false;
	} catch (e) {
		console.error('Error saving to origin:', e);
		return false;
	} finally {
		setLoading(false);
	}
}

/**
 * Sauvegarde dans l'origine sans popup (Cmd+Shift+S)
 */
export async function saveToOriginDirect(panelId: 'left' | 'right') {
	const panel = getPanel(panelId);

	// Annuler l'auto-save en cours
	if (panel.autoSaveTimer) {
		clearTimeout(panel.autoSaveTimer);
		panel.autoSaveTimer = null;
	}

	if (!panel.isModified) {
		showToast('Aucune modification à sauvegarder', 'warning');
		return;
	}

	const modifiedIncludes = detectModifiedIncludes(panelId);

	if (modifiedIncludes.length === 0) {
		// Pas d'includes modifiés, sauvegarde normale
		await manualSave(panelId);
		return;
	}

	setLoading(true, 'Sauvegarde dans les fichiers sources...');

	const saved = await saveIncludesToOrigin(panelId);
	if (saved) {
		setLoading(true, 'Build...');
		await buildAgent(panelId);
		showToast(`${modifiedIncludes.length} include(s) sauvegardé(s) dans l'origine`, 'success');
	} else {
		showToast('Erreur lors de la sauvegarde', 'error');
	}

	setLoading(false);
}

/**
 * Sauvegarde dans l'origine et rebuild tous les dépendants (Cmd+Option+S)
 */
export async function saveAndRebuildAll(panelId: 'left' | 'right') {
	const panel = getPanel(panelId);

	// Annuler l'auto-save en cours
	if (panel.autoSaveTimer) {
		clearTimeout(panel.autoSaveTimer);
		panel.autoSaveTimer = null;
	}

	if (!panel.isModified) {
		showToast('Aucune modification à sauvegarder', 'warning');
		return;
	}

	const modifiedIncludes = detectModifiedIncludes(panelId);

	if (modifiedIncludes.length === 0) {
		// Pas d'includes modifiés, sauvegarde normale
		await manualSave(panelId);
		return;
	}

	setLoading(true, 'Sauvegarde dans les fichiers sources...');

	const saved = await saveIncludesToOrigin(panelId);
	if (!saved) {
		showToast('Erreur lors de la sauvegarde', 'error');
		setLoading(false);
		return;
	}

	// Récupérer les dépendants
	setLoading(true, 'Recherche des fichiers dépendants...');
	const dependents = await fetchDependents(panel.project!, modifiedIncludes);

	// Build le fichier actuel
	setLoading(true, 'Build du fichier actuel...');
	await buildAgent(panelId);

	// Build tous les fichiers dépendants
	if (dependents.length > 0) {
		setLoading(true, `Build de ${dependents.length} fichier(s) dépendant(s)...`);
		// Pour l'instant, on fait un build global du projet
		// TODO: Optimiser pour ne builder que les fichiers concernés
		await fetch('/api/build', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ project: panel.project, export: true })
		});
	}

	showToast(
		`${modifiedIncludes.length} include(s) sauvegardé(s), ${dependents.length + 1} fichier(s) rebuildé(s)`,
		'success'
	);

	setLoading(false);
}

/**
 * Remplace les includes par leur contenu (supprime les marqueurs include)
 * Utilisé quand l'utilisateur choisit "Copier ici"
 */
export async function copyIncludesToLocal(panelId: 'left' | 'right') {
	const panel = getPanel(panelId);

	if (!panel.project || !panel.agent || !panel.currentSection) {
		return false;
	}

	// Le contenu actuel a déjà les includes expandés avec marqueurs
	// On doit simplement retirer les marqueurs et garder le contenu
	let newContent = panel.content;

	// Supprimer les marqueurs start/end mais garder le contenu
	newContent = newContent.replace(/<!-- @include-start: [^>]+ -->\n/g, '');
	newContent = newContent.replace(/\n<!-- @include-end: [^>]+ -->/g, '');

	// Mettre à jour le panneau
	panel.content = newContent;
	panel.isExpanded = false;
	panel.hasIncludes = false;
	panel.collapsedContent = newContent;
	panel.isModified = true;

	// Sauvegarder
	const saved = await saveSection(panelId);
	if (saved) {
		await buildAgent(panelId);
		showToast('Contenu copié localement, includes supprimés', 'success');
	}

	return saved;
}
