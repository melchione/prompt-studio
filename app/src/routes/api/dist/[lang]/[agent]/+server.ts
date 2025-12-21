import { json } from '@sveltejs/kit';
import fs from 'fs/promises';
import path from 'path';

const PROJECTS_DIR = path.resolve('..', 'projects');

export async function GET({ params, url }) {
	const { lang, agent } = params;
	const project = url.searchParams.get('project');

	if (!project) {
		return json({ content: '', error: 'Project query param required' }, { status: 400 });
	}

	const distPath = path.join(PROJECTS_DIR, project, 'dist', lang, `${agent}.md`);

	try {
		const content = await fs.readFile(distPath, 'utf-8');
		return json({ content });
	} catch (error) {
		console.error(`Error reading dist for ${agent}:`, error);
		return json({ content: '', error: 'Dist file not found' }, { status: 404 });
	}
}
