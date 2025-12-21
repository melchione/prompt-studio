import { json } from '@sveltejs/kit';
import { spawn } from 'child_process';
import path from 'path';

const TOOLS_DIR = path.resolve('..', 'tools');

interface CollapseRequest {
	content: string;
	lang?: string;
}

interface CollapseResponse {
	content: string;
	modifiedFiles?: Record<string, string>;
	error?: string;
}

/**
 * POST /api/collapse
 *
 * Collapse expanded includes back to {% include %} directives.
 * Returns the collapsed content and a dict of modified include files.
 *
 * Body: { content: string, lang?: string }
 * Returns: { content: string, modifiedFiles?: {...}, error?: string }
 */
export async function POST({ request }) {
	try {
		const body: CollapseRequest = await request.json();
		const { content, lang } = body;

		if (!content) {
			return json({ content: '', error: 'Content required' }, { status: 400 });
		}

		const result = await new Promise<CollapseResponse>((resolve) => {
			const proc = spawn(
				'python3',
				['expand.py', 'collapse-stdin', '--lang', lang || 'fr'],
				{
					cwd: TOOLS_DIR,
					env: { ...process.env }
				}
			);

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
					try {
						const parsed = JSON.parse(stdout);
						resolve({
							content: parsed.content || '',
							modifiedFiles: parsed.modifiedFiles || {}
						});
					} catch {
						resolve({ content, error: 'Failed to parse response' });
					}
				} else {
					resolve({ content, error: stderr || 'Collapse failed' });
				}
			});

			proc.on('error', (err) => {
				resolve({ content, error: err.message });
			});
		});

		return json(result);
	} catch (error) {
		console.error('Collapse error:', error);
		return json({ content: '', error: 'Collapse failed' }, { status: 500 });
	}
}
