# /ps:editor - Lancer l'interface web

Lance le serveur de l'éditeur web Prompt Studio.

## Usage

```
/ps:editor [--port PORT]
```

## Instructions

Exécuter la commande suivante :

```bash
python tools/server.py --port 8236
```

Afficher ensuite :

```
🌐 PROMPT STUDIO - Éditeur Web
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Serveur démarré !

📍 URL : http://localhost:8236

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

- Le serveur utilise le port 8236 par défaut
- L'API est disponible sur `/api/`
- Les fichiers statiques sont servis depuis `editor/`

## Résumé et Prochaines Étapes

À l'affichage de l'éditeur, afficher :

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ÉDITEUR WEB LANCÉ

📋 Ce qui a été fait :
   • Serveur démarré sur le port {port}
   • API REST disponible
   • Interface web accessible

📍 URL : http://localhost:{port}

⌨️  Raccourcis disponibles :
   • Ctrl+S : Sauvegarder
   • Ctrl+I : Insérer include
   • Escape : Fermer modales

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 COMMANDES DISPONIBLES (dans un autre terminal)

    /ps:build            Compiler les prompts
    /ps:validate         Valider le prompt
    /ps:status           Voir l'état du projet

⚠️  Pour arrêter le serveur : Ctrl+C
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
