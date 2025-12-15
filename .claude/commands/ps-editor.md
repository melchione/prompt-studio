# /ps:editor - Lancer l'interface web

Lance le serveur de l'éditeur web Prompt Studio.

## Usage

```
/ps:editor [--port PORT]
```

## Instructions

Exécuter la commande suivante :

```bash
python tools/server.py --port 8080
```

Afficher ensuite :

```
🌐 PROMPT STUDIO - Éditeur Web
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Serveur démarré !

📍 URL : http://localhost:8080

Fonctionnalités :
- Sélection projet/agent
- Édition des sections avec Monaco Editor
- Insertion d'includes (Ctrl+I)
- Switch FR/EN
- Build intégré

⌨️  Raccourcis clavier :
- Ctrl+S : Sauvegarder
- Ctrl+I : Insérer un include
- Escape : Fermer les modales

Pour arrêter : Ctrl+C
```

## Notes

- Le serveur utilise le port 8080 par défaut
- L'API est disponible sur `/api/`
- Les fichiers statiques sont servis depuis `editor/`
