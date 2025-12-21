import { json } from '@sveltejs/kit';
import fs from 'fs/promises';
import path from 'path';

const PROJECTS_DIR = path.resolve('..', 'projects');

export async function POST({ params, request }) {
	const { project, agent, lang } = params;

	try {
		const body = await request.json();
		const { section } = body; // Nom du fichier à supprimer

		if (!section) {
			return json({ success: false, error: 'Section name required' }, { status: 400 });
		}

		const langPath = path.join(PROJECTS_DIR, project, 'agents', agent, lang);
		const filePath = path.join(langPath, section);

		// Vérifier que le fichier existe
		try {
			await fs.access(filePath);
		} catch {
			return json({ success: false, error: 'Section not found' }, { status: 404 });
		}

		// Supprimer le fichier
		await fs.unlink(filePath);

		// Renuméroter les fichiers restants
		const files = await fs.readdir(langPath);
		const mdFiles = files.filter((f) => f.endsWith('.md')).sort();

		const renames: Array<{ from: string; to: string }> = [];
		for (let i = 0; i < mdFiles.length; i++) {
			const oldName = mdFiles[i];
			const newPrefix = String(i + 1).padStart(2, '0');
			const baseName = oldName.replace(/^\d+-/, '');
			const newName = `${newPrefix}-${baseName}`;

			if (oldName !== newName) {
				renames.push({ from: oldName, to: newName });
			}
		}

		// Renommer en deux phases pour éviter les conflits
		for (const rename of renames) {
			const tempName = `_temp_${rename.to}`;
			await fs.rename(path.join(langPath, rename.from), path.join(langPath, tempName));
		}
		for (const rename of renames) {
			const tempName = `_temp_${rename.to}`;
			await fs.rename(path.join(langPath, tempName), path.join(langPath, rename.to));
		}

		// Récupérer la nouvelle liste
		const newFiles = await fs.readdir(langPath);
		const sections = newFiles
			.filter((f) => f.endsWith('.md'))
			.sort()
			.map((name, index) => ({ name, order: index }));

		return json({ success: true, sections });
	} catch (error) {
		console.error('Error deleting section:', error);
		return json({ success: false, error: 'Failed to delete section' }, { status: 500 });
	}
}
