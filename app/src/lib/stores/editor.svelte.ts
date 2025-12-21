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

// Modales
export const modals = $state({
	createSection: { open: false, panelId: null as 'left' | 'right' | null },
	deleteConfirm: { open: false, section: null as string | null, panelId: null as 'left' | 'right' | null },
	insertInclude: { open: false, panelId: null as 'left' | 'right' | null, cursorLine: 1, cursorColumn: 1 },
	translate: { open: false, panelId: null as 'left' | 'right' | null }
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
