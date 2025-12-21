import { json } from '@sveltejs/kit';
import fs from 'fs/promises';
import path from 'path';

const PROJECTS_DIR = path.resolve('..', 'projects');

export async function GET({ params }) {
	const { project, agent, lang, section } = params;
	const sectionPath = path.join(PROJECTS_DIR, project, 'agents', agent, lang, section);

	try {
		const content = await fs.readFile(sectionPath, 'utf-8');
		return json({ content });
	} catch (error) {
		console.error(`Error loading section ${section}:`, error);
		return json({ content: '', error: 'Section not found' }, { status: 404 });
	}
}

export async function POST({ params, request }) {
	const { project, agent, lang, section } = params;
	const sectionPath = path.join(PROJECTS_DIR, project, 'agents', agent, lang, section);

	try {
		const body = await request.json();
		const content = body.content || '';

		// S'assurer que le dossier existe
		const dirPath = path.dirname(sectionPath);
		await fs.mkdir(dirPath, { recursive: true });

		// Écrire le fichier
		await fs.writeFile(sectionPath, content, 'utf-8');

		return json({ success: true });
	} catch (error) {
		console.error(`Error saving section ${section}:`, error);
		return json({ success: false, error: 'Failed to save section' }, { status: 500 });
	}
}
