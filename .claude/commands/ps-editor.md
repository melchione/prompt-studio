# /ps:editor - Lancer l'interface web

Lance le serveur de l'éditeur web Prompt Studio.

## Usage

```
/ps:editor [--port PORT]
```

## Instructions

### Étape 1 : Vérifier et arrêter le serveur existant

D'abord, vérifier si un serveur tourne déjà sur le port 8236 :

```bash
lsof -i :8236
```

Si un processus est trouvé, l'arrêter :

```bash
pkill -f "tools/server.py" 2>/dev/null || true
sleep 1
```

### Étape 2 : Lancer le serveur

Exécuter la commande suivante en background :

```bash
python tools/server.py --port 8236 &
```

### Étape 3 : Vérifier le démarrage

Attendre et vérifier que le serveur a démarré :

```bash
sleep 2 && lsof -i :8236
```

### Étape 4 : Ouvrir le navigateur

```bash
open http://localhost:8236
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
