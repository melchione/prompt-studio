import { json } from '@sveltejs/kit';
import fs from 'fs/promises';
import path from 'path';

const PROJECTS_DIR = path.resolve('..', 'projects');

export async function GET({ params }) {
	const { project, agent } = params;
	const agentPath = path.join(PROJECTS_DIR, project, 'agents', agent);

	try {
		const sections: Record<string, Array<{ name: string; order: number }>> = {
			fr: [],
			en: []
		};

		for (const lang of ['fr', 'en']) {
			const langPath = path.join(agentPath, lang);
			try {
				const files = await fs.readdir(langPath);
				const mdFiles = files
					.filter((f) => f.endsWith('.md'))
					.sort()
					.map((name, index) => ({ name, order: index }));
				sections[lang] = mdFiles;
			} catch {
				// Dossier langue non trouvé
			}
		}

		return json({ sections });
	} catch (error) {
		console.error(`Error loading agent ${agent}:`, error);
		return json({ sections: { fr: [], en: [] }, error: 'Failed to load agent' }, { status: 500 });
	}
}
