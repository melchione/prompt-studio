import { json } from '@sveltejs/kit';
import { spawn } from 'child_process';
import path from 'path';

const TOOLS_DIR = path.resolve('..', 'tools');

export async function POST({ request }) {
	try {
		const body = await request.json();
		const { project, lang, content } = body;

		if (!content) {
			return json({ content: '', error: 'Content required' }, { status: 400 });
		}

		if (!project) {
			return json({ content: '', error: 'Project required' }, { status: 400 });
		}

		// Utiliser expand.py expand-stdin pour résoudre les includes
		const result = await new Promise<{ content: string; error?: string }>((resolve) => {
			const proc = spawn('python3', [
				'expand.py',
				'expand-stdin',
				'--project', project,
				'--lang', lang || 'fr'
			], {
				cwd: TOOLS_DIR,
				env: { ...process.env }
			});

			let stdout = '';
			let stderr = '';

			proc.stdout.on('data', (data) => {
				stdout += data.toString();
			});

			proc.stderr.on('data', (data) => {
				stderr += data.toString();
			});

			proc.stdin.write(content);
			proc.stdin.end();

			proc.on('close', (code) => {
				if (code === 0) {
					resolve({ content: stdout });
				} else {
					resolve({ content, error: stderr || 'Expand failed' });
				}
			});

			proc.on('error', (err) => {
				resolve({ content, error: err.message });
			});
		});

		return json(result);
	} catch (error) {
		console.error('Expand error:', error);
		return json({ content: '', error: 'Expand failed' }, { status: 500 });
	}
}
