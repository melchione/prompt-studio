import { json } from '@sveltejs/kit';
import fs from 'fs/promises';
import path from 'path';

const STATE_FILE = path.resolve('.state.json');

export async function GET() {
	try {
		const content = await fs.readFile(STATE_FILE, 'utf-8');
		return json(JSON.parse(content));
	} catch {
		// État par défaut
		return json({
			active_project: null,
			active_agent: null,
			phase: null,
			current_section: null
		});
	}
}

export async function POST({ request }) {
	try {
		const body = await request.json();

		// Lire l'état existant
		let state = {};
		try {
			const content = await fs.readFile(STATE_FILE, 'utf-8');
			state = JSON.parse(content);
		} catch {
			// Fichier n'existe pas encore
		}

		// Fusionner avec les nouvelles valeurs
		const newState = { ...state, ...body };

		// Sauvegarder
		await fs.writeFile(STATE_FILE, JSON.stringify(newState, null, 2), 'utf-8');

		return json({ success: true, state: newState });
	} catch (error) {
		console.error('Error saving state:', error);
		return json({ success: false, error: 'Failed to save state' }, { status: 500 });
	}
}
