import { json } from '@sveltejs/kit';
import fs from 'fs/promises';
import path from 'path';

const PROJECTS_DIR = path.resolve('..', 'projects');

export async function POST({ params, request }) {
	const { project, agent } = params;

	try {
		const body = await request.json();
		const { lang, order } = body; // order = ['02-xxx.md', '01-yyy.md', '03-zzz.md']

		if (!lang || !order || !Array.isArray(order)) {
			return json({ success: false, error: 'lang and order array required' }, { status: 400 });
		}

		const langPath = path.join(PROJECTS_DIR, project, 'agents', agent, lang);

		// Renommer les fichiers avec des noms temporaires
		const tempRenames: Array<{ from: string; to: string; finalName: string }> = [];

		for (let i = 0; i < order.length; i++) {
			const oldName = order[i];
			const newPrefix = String(i + 1).padStart(2, '0');
			const baseName = oldName.replace(/^\d+-/, '');
			const newName = `${newPrefix}-${baseName}`;

			if (oldName !== newName) {
				const tempName = `_temp_${i}_${baseName}`;
				tempRenames.push({
					from: oldName,
					to: tempName,
					finalName: newName
				});
			}
		}

		// Phase 1: Renommer vers temp
		for (const rename of tempRenames) {
			await fs.rename(path.join(langPath, rename.from), path.join(langPath, rename.to));
		}

		// Phase 2: Renommer vers final
		for (const rename of tempRenames) {
			await fs.rename(path.join(langPath, rename.to), path.join(langPath, rename.finalName));
		}

		// Récupérer la nouvelle liste
		const files = await fs.readdir(langPath);
		const sections = files
			.filter((f) => f.endsWith('.md'))
			.sort()
			.map((name, index) => ({ name, order: index }));

		return json({ success: true, sections });
	} catch (error) {
		console.error('Error reordering sections:', error);
		return json({ success: false, error: 'Failed to reorder sections' }, { status: 500 });
	}
}
