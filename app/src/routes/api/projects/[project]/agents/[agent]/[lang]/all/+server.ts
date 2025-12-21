import { json } from '@sveltejs/kit';
import fs from 'fs/promises';
import path from 'path';

const PROJECTS_DIR = path.resolve('..', 'projects');

export async function GET({ params }) {
	const { project, agent, lang } = params;
	const langPath = path.join(PROJECTS_DIR, project, 'agents', agent, lang);

	try {
		const files = await fs.readdir(langPath);
		const mdFiles = files.filter((f) => f.endsWith('.md')).sort();

		const sections: Record<string, string> = {};
		const order: string[] = [];

		for (const file of mdFiles) {
			const filePath = path.join(langPath, file);
			const content = await fs.readFile(filePath, 'utf-8');
			sections[file] = content;
			order.push(file);
		}

		return json({ sections, order });
	} catch (error) {
		console.error(`Error loading all sections:`, error);
		return json({ sections: {}, order: [], error: 'Failed to load sections' }, { status: 500 });
	}
}
