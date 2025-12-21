import { json } from '@sveltejs/kit';
import fs from 'fs/promises';
import path from 'path';

const PROJECTS_DIR = path.resolve('..', 'projects');

interface IncludeItem {
	project: string;
	agent: string;
	lang: string;
	section: string;
	path: string;
}

export async function GET() {
	try {
		const includes: IncludeItem[] = [];

		// Parcourir tous les projets
		const projectEntries = await fs.readdir(PROJECTS_DIR, { withFileTypes: true });

		for (const projectEntry of projectEntries) {
			if (!projectEntry.isDirectory() || projectEntry.name.startsWith('.')) continue;

			const projectName = projectEntry.name;
			const agentsPath = path.join(PROJECTS_DIR, projectName, 'agents');

			try {
				const agentEntries = await fs.readdir(agentsPath, { withFileTypes: true });

				for (const agentEntry of agentEntries) {
					if (!agentEntry.isDirectory() || agentEntry.name.startsWith('.')) continue;

					const agentName = agentEntry.name;

					for (const lang of ['fr', 'en']) {
						const langPath = path.join(agentsPath, agentName, lang);

						try {
							const files = await fs.readdir(langPath);
							const mdFiles = files.filter((f) => f.endsWith('.md'));

							for (const file of mdFiles) {
								includes.push({
									project: projectName,
									agent: agentName,
									lang,
									section: file,
									path: `${agentName}/${lang}/${file}`
								});
							}
						} catch {
							// Dossier lang n'existe pas
						}
					}
				}
			} catch {
				// Pas de dossier agents
			}
		}

		return json({ includes });
	} catch (error) {
		console.error('Error listing includes:', error);
		return json({ includes: [], error: 'Failed to list includes' }, { status: 500 });
	}
}
