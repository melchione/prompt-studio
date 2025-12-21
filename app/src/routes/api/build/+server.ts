import { json } from '@sveltejs/kit';
import { spawn } from 'child_process';
import path from 'path';

const TOOLS_DIR = path.resolve('..', 'tools');

export async function POST({ request }) {
	try {
		const body = await request.json();
		const { project, export: doExport = false } = body;

		if (!project) {
			return json({ success: false, error: 'Project name required' }, { status: 400 });
		}

		const args = ['build.py', '--project', project];
		if (doExport) {
			args.push('--export');
		}

		const result = await new Promise<{ success: boolean; output: string; error?: string }>(
			(resolve) => {
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
						resolve({ success: true, output: stdout });
					} else {
						resolve({ success: false, output: stdout, error: stderr || 'Build failed' });
					}
				});

				proc.on('error', (err) => {
					resolve({ success: false, output: '', error: err.message });
				});
			}
		);

		return json(result);
	} catch (error) {
		console.error('Build error:', error);
		return json({ success: false, error: 'Build failed' }, { status: 500 });
	}
}
