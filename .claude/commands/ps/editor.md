# /ps:editor - Lancer l'interface web

Lance le serveur de l'éditeur web Prompt Studio.

## Usage

```
/ps:editor
```

## Instructions

Exécuter les commandes suivantes dans cet ordre :

### 1. Vérifier si le serveur tourne déjà

```bash
lsof -i :8236
```

### 2. Si le port N'EST PAS utilisé (exit code 1), lancer le serveur

```bash
python /Users/melkione/Projets/Cowai/prompt-studio/tools/server.py --port 8236
```

**IMPORTANT** : Lancer cette commande en background (`run_in_background: true`)

### 3. Attendre et vérifier

```bash
sleep 2 && lsof -i :8236
```

Si le port est maintenant utilisé, continuer. Sinon, afficher l'erreur.

### 4. Ouvrir le navigateur

```bash
open http://localhost:8236
```

## Si le serveur tourne déjà

Si l'étape 1 montre qu'un processus utilise le port 8236, simplement ouvrir le navigateur :

```bash
open http://localhost:8236
```

## Message de confirmation

Afficher :

```
🌐 PROMPT STUDIO - Éditeur Web
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Serveur actif sur http://localhost:8236

⌨️  Raccourcis :
   • Ctrl+S : Sauvegarder
   • Ctrl+I : Insérer include

Pour arrêter : pkill -f "tools/server.py"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Notes

- Port par défaut : 8236
- API : `/api/`
- Fichiers statiques : `editor/`
