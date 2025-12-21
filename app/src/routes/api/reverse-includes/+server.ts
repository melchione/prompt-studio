import { json } from '@sveltejs/kit';
import { spawn } from 'child_process';
import path from 'path';

const TOOLS_DIR = path.resolve('..', 'tools');

interface ReverseIncludesRequest {
	project: string;
	targetFile: string;
	lang?: string;
}

interface Dependent {
	project: string;
	agent: string;
	lang: string;
	section: string;
	full_path: string;
}

interface ReverseIncludesResponse {
	dependents: Dependent[];
	error?: string;
}

/**
 * POST /api/reverse-includes
 *
 * Find all files that include a given target file.
 *
 * Body: { project: string, targetFile: string, lang?: string }
 * Returns: { dependents: [...], error?: string }
 */
export async function POST({ request }) {
	try {
		const body: ReverseIncludesRequest = await request.json();
		const { project, targetFile, lang } = body;

		if (!project) {
			return json({ dependents: [], error: 'Project required' }, { status: 400 });
		}

		if (!targetFile) {
			return json({ dependents: [], error: 'Target file required' }, { status: 400 });
		}

		// Build arguments for expand.py reverse-includes command
		const args = [
			'expand.py',
			'reverse-includes',
			'--project',
			project,
			'--target',
			targetFile,
			'--json'
		];

		// Add optional language filter
		if (lang) {
			args.push('--lang', lang);
		}

		const result = await new Promise<ReverseIncludesResponse>((resolve) => {
			const proc = spawn('python3', args, {
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

			proc.on('close', (code) => {
				if (code === 0) {
					try {
						const parsed = JSON.parse(stdout);
						resolve({ dependents: parsed.dependents || [] });
					} catch {
						resolve({ dependents: [], error: 'Failed to parse response' });
					}
				} else {
					resolve({ dependents: [], error: stderr || 'Reverse includes lookup failed' });
				}
			});

			proc.on('error', (err) => {
				resolve({ dependents: [], error: err.message });
			});
		});

		return json(result);
	} catch (error) {
		console.error('Reverse includes error:', error);
		return json({ dependents: [], error: 'Reverse includes lookup failed' }, { status: 500 });
	}
}
