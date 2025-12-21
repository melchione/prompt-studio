// Types pour Prompt Studio

export interface Project {
	name: string;
	version: string;
	agents_count: number;
	default_language?: string;
	export_path?: string;
	created_at?: string;
}

export interface Agent {
	name: string;
	languages: ('fr' | 'en')[];
	sections: {
		fr: Section[];
		en: Section[];
	};
}

export interface Section {
	name: string;
	words: number;
	size: number;
}

export interface SectionContent {
	project: string;
	agent: string;
	language: string;
	section: string;
	content: string;
	words: number;
}

export interface SectionBoundary {
	section: string;
	delimiterLine: number;
	startLine: number;
	endLine: number;
}

export interface PanelState {
	project: string | null;
	agent: string | null;
	lang: 'fr' | 'en';
	sections: Section[];
	currentSection: string | null;
	content: string;
	originalContent: string;
	collapsedContent: string;
	sectionBoundaries: SectionBoundary[];
	hasIncludes: boolean;
	isModified: boolean;
	isExpanded: boolean;
	viewMode: 'editor' | 'preview' | 'diff';
	autoSaveTimer: ReturnType<typeof setTimeout> | null;
	lastSaved: Date | null;
}

export interface Toast {
	id: number;
	message: string;
	type: 'success' | 'error' | 'warning';
}

export interface ModalState {
	open: boolean;
	panelId: 'left' | 'right' | null;
}

export interface Include {
	project: string;
	agent: string;
	language: string;
	section: string;
	ref: string;
}

export interface BuildResult {
	success: boolean;
	output: string;
	error?: string;
	exported: boolean;
}

export interface AppState {
	active_project: string | null;
	active_agent: string | null;
	phase: string | null;
	current_section: string | null;
	last_build: string | null;
	projects: string[];
}
