import { json } from '@sveltejs/kit';
import fs from 'fs/promises';
import path from 'path';

const PROJECTS_DIR = path.resolve('..', 'projects');

export async function GET() {
	try {
		const entries = await fs.readdir(PROJECTS_DIR, { withFileTypes: true });
		const projects = [];

		for (const entry of entries) {
			if (entry.isDirectory() && !entry.name.startsWith('.')) {
				const projectPath = path.join(PROJECTS_DIR, entry.name);
				const configPath = path.join(projectPath, '.project.json');

				let config = { version: '1.0.0', agents: [] };
				try {
					const configContent = await fs.readFile(configPath, 'utf-8');
					config = JSON.parse(configContent);
				} catch {
					// Config par défaut si non trouvée
				}

				// Compter les agents
				const agentsPath = path.join(projectPath, 'agents');
				let agentsCount = 0;
				try {
					const agentEntries = await fs.readdir(agentsPath, { withFileTypes: true });
					agentsCount = agentEntries.filter((e) => e.isDirectory()).length;
				} catch {
					// Pas de dossier agents
				}

				projects.push({
					name: entry.name,
					version: config.version || '1.0.0',
					agents_count: agentsCount
				});
			}
		}

		return json({ projects });
	} catch (error) {
		console.error('Error loading projects:', error);
		return json({ projects: [], error: 'Failed to load projects' }, { status: 500 });
	}
}
