import { json } from '@sveltejs/kit';
import fs from 'fs/promises';
import path from 'path';

const PROJECTS_DIR = path.resolve('..', 'projects');

export async function POST({ params, request }) {
	const { project, agent, lang } = params;

	try {
		const body = await request.json();
		const { name } = body; // Nom de la section (sans numéro)

		if (!name) {
			return json({ success: false, error: 'Section name required' }, { status: 400 });
		}

		const langPath = path.join(PROJECTS_DIR, project, 'agents', agent, lang);

		// S'assurer que le dossier existe
		await fs.mkdir(langPath, { recursive: true });

		// Trouver le prochain numéro
		const files = await fs.readdir(langPath);
		const mdFiles = files.filter((f) => f.endsWith('.md')).sort();
		const nextNum = mdFiles.length + 1;
		const prefix = String(nextNum).padStart(2, '0');

		// Nettoyer le nom
		const cleanName = name
			.toLowerCase()
			.replace(/[^a-z0-9]+/g, '-')
			.replace(/^-|-$/g, '');
		const fileName = `${prefix}-${cleanName}.md`;
		const filePath = path.join(langPath, fileName);

		// Créer le fichier avec un contenu initial
		const initialContent = `# ${name}\n\n`;
		await fs.writeFile(filePath, initialContent, 'utf-8');

		return json({
			success: true,
			section: { name: fileName, order: nextNum - 1 }
		});
	} catch (error) {
		console.error('Error creating section:', error);
		return json({ success: false, error: 'Failed to create section' }, { status: 500 });
	}
}
