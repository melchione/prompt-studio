import { json } from '@sveltejs/kit';
import fs from 'fs/promises';
import path from 'path';

const PROJECTS_DIR = path.resolve('..', 'projects');

export async function GET({ params }) {
	const { project } = params;
	const agentsPath = path.join(PROJECTS_DIR, project, 'agents');

	try {
		const entries = await fs.readdir(agentsPath, { withFileTypes: true });
		const agents = [];

		for (const entry of entries) {
			if (entry.isDirectory() && !entry.name.startsWith('.')) {
				agents.push({ name: entry.name });
			}
		}

		return json({ agents });
	} catch (error) {
		console.error(`Error loading agents for ${project}:`, error);
		return json({ agents: [], error: 'Failed to load agents' }, { status: 500 });
	}
}
